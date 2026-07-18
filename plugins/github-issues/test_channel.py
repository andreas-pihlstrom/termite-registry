import io
import unittest
from unittest import mock
import channel


class FakeTermite:
    def __init__(self): self.items, self.acks, self.queued = [], [], None
    def ingest(self, item): self.items.append(item)
    def reply_is_queued(self, reply_id): return self.queued is None or reply_id in self.queued
    def acknowledge(self, *args):
        self.acks.append(args)
        if self.queued is not None: self.queued.discard(args[0])
class FakeGitHub:
    def __init__(self, issues=None, comments=None, error=None):
        self.issue_values, self.comment_values, self.error = issues or [], comments or [], error
        self.sends = []
    def issues(self, repository, since): return self.issue_values
    def comments(self, repository, since): return self.comment_values
    def send(self, reply):
        if self.error: raise channel.ConnectorError(self.error)
        self.sends.append(reply)


class GitHubTests(unittest.TestCase):
    def test_oversized_http_response_is_rejected(self):
        with mock.patch.object(channel, "MAX_HTTP_BYTES", 4):
            with self.assertRaises(channel.ConnectorError): channel.read_json(io.BytesIO(b"12345"), "test")

    def test_explicit_repository_allowlist(self):
        with self.assertRaises(channel.ConnectorError): channel.parse_repositories("")
        with self.assertRaises(channel.ConnectorError): channel.parse_repositories("https://github.com/a/b")
        self.assertEqual(channel.parse_repositories("b/two,a/one"), ["a/one", "b/two"])
    def test_issues_comments_and_pr_filter(self):
        issues = [
            {"id": 10, "number": 3, "title": "Broken", "body": "Please fix", "created_at": "2026-01-01T00:00:00Z",
             "updated_at": "2026-01-01T00:01:00Z", "user": {"id": 2, "login": "mira"}},
            {"id": 11, "number": 4, "title": "PR", "pull_request": {}, "updated_at": "2026-01-01T00:02:00Z"},
        ]
        comments = [{"id": 20, "body": "More detail", "issue_url": "https://api.github.com/repos/a/b/issues/3",
            "created_at": "2026-01-01T00:03:00Z", "updated_at": "2026-01-01T00:03:00Z", "user": {"id": 3, "login": "lee"}}]
        termite = FakeTermite(); connector = channel.GitHubConnector(termite, FakeGitHub(issues, comments), ["a/b"], "", 30, 10)
        connector.poll_once()
        self.assertEqual([x["deliveryID"] for x in termite.items], ["github:issue:10", "github:comment:20"])
        self.assertEqual(termite.items[1]["replyToID"], "3")
    def test_self_and_bot_actors_are_filtered(self):
        issues = [
            {"id": 10, "number": 1, "title": "Self", "updated_at": "2026-01-01T00:01:00Z",
             "user": {"id": 2, "login": "TermiteUser"}},
            {"id": 11, "number": 2, "title": "Bot", "updated_at": "2026-01-01T00:02:00Z",
             "user": {"id": 3, "login": "release-bot", "type": "Bot"}},
            {"id": 12, "number": 3, "title": "App", "updated_at": "2026-01-01T00:03:00Z",
             "user": {"id": 4, "login": "checks[bot]"}},
        ]
        termite = FakeTermite(); connector = channel.GitHubConnector(termite, FakeGitHub(issues, []), ["a/b"], "", 30, 10)
        connector.own_login = "termiteuser"
        connector.poll_once()
        self.assertEqual(termite.items, [])
    def test_allowlist_blocks_outbound(self):
        termite = FakeTermite(); github = FakeGitHub()
        connector = channel.GitHubConnector(termite, github, ["a/b"], "", 30, 10)
        connector.deliver({"id": "r1", "conversationID": "evil/repo", "replyToID": "1", "body": "done"})
        self.assertFalse(github.sends)
        self.assertEqual(termite.acks[0][1], False)
    def test_provider_failure_is_acknowledged(self):
        termite = FakeTermite(); connector = channel.GitHubConnector(termite, FakeGitHub(error="denied"), ["a/b"], "", 30, 10)
        connector.deliver({"id": "r2", "conversationID": "a/b", "replyToID": "1", "body": "done"})
        self.assertEqual(termite.acks, [("r2", False, "denied")])
    def test_stale_recovery_copy_is_not_sent_or_acked_twice(self):
        termite = FakeTermite(); termite.queued = {"r1"}; github = FakeGitHub()
        connector = channel.GitHubConnector(termite, github, ["a/b"], "", 30, 10)
        reply = {"id": "r1", "conversationID": "a/b", "replyToID": "1", "body": "done"}
        connector.deliver(reply); connector.deliver(reply)
        self.assertEqual(len(github.sends), 1)
        self.assertEqual(termite.acks, [("r1", True)])
    def test_marker_is_stable(self):
        self.assertEqual(channel.GitHubClient.marker("r1"), channel.GitHubClient.marker("r1"))
        self.assertNotEqual(channel.GitHubClient.marker("r1"), channel.GitHubClient.marker("r2"))


if __name__ == "__main__": unittest.main()
