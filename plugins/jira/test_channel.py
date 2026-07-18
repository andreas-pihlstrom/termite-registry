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
class FakeJira:
    def __init__(self, issues=None, comments=None, error=None): self.issue_values, self.comment_values, self.error, self.sent = issues or [], comments or [], error, []
    def issues(self, projects, since): return self.issue_values
    def recent_comments(self, issue_key, since): return self.comment_values
    def send_comment(self, issue_key, body):
        if self.error: raise channel.ConnectorError(self.error)
        self.sent.append((issue_key, body))


class JiraTests(unittest.TestCase):
    def test_oversized_http_response_is_rejected(self):
        with mock.patch.object(channel, "MAX_HTTP_BYTES", 4):
            with self.assertRaises(channel.ConnectorError): channel.read_json(io.BytesIO(b"12345"), "test")

    def test_strict_cloud_origin_and_projects(self):
        self.assertEqual(channel.validate_base_url("https://acme.atlassian.net/"), "https://acme.atlassian.net")
        for bad in ["http://acme.atlassian.net", "https://evil.example", "https://acme.atlassian.net/path"]:
            with self.assertRaises(channel.ConnectorError): channel.validate_base_url(bad)
        self.assertEqual(channel.parse_projects("eng,OPS"), ["ENG", "OPS"])
    def test_adf_text_and_document(self):
        doc = {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Hello"}]}]}
        self.assertEqual(channel.adf_text(doc).strip(), "Hello")
        self.assertEqual(channel.adf_document("a\nb")["content"][1]["content"][0]["text"], "b")
    def test_recent_comments_pages_without_silent_drop(self):
        client = object.__new__(channel.JiraClient)
        pages = [
            {"comments": [{"id": str(i), "created": "2026-01-02T00:00:00Z"} for i in range(100)], "total": 101},
            {"comments": [{"id": "last", "created": "2026-01-01T12:00:00Z"}], "total": 101},
        ]
        client.call = mock.Mock(side_effect=pages)
        found = client.recent_comments("ENG-7", channel.datetime(2026, 1, 1, tzinfo=channel.timezone.utc))
        self.assertEqual(len(found), 101)
        self.assertEqual(client.call.call_count, 2)
    def test_recent_comment_overflow_fails_instead_of_dropping(self):
        client = object.__new__(channel.JiraClient)
        client.call = mock.Mock(return_value={"comments": [
            {"id": str(i), "created": "2026-01-02T00:00:00Z"} for i in range(100)], "total": 101})
        with self.assertRaises(channel.ConnectorError):
            client.recent_comments("ENG-7", channel.datetime(2026, 1, 1, tzinfo=channel.timezone.utc), max_pages=1)
    def test_issue_and_comment_become_work(self):
        issue = {"id": "10", "key": "ENG-7", "fields": {"summary": "Fix", "created": "2026-01-01T00:00:00Z",
            "description": {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Details"}]}]},
            "reporter": {"accountId": "u1", "displayName": "Mira"}}}
        comment = {"id": "20", "created": "2026-01-01T00:01:00Z", "author": {"accountId": "u2", "displayName": "Lee"},
            "body": {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "More"}]}]}}
        termite = FakeTermite(); connector = channel.JiraConnector(termite, FakeJira([issue], [comment]), ["ENG"], "", 60, 10)
        connector.poll_once()
        self.assertEqual([item["deliveryID"] for item in termite.items], ["jira:issue:10", "jira:comment:20"])
    def test_outbound_allowlist_and_failure(self):
        termite = FakeTermite(); jira = FakeJira(error="denied")
        connector = channel.JiraConnector(termite, jira, ["ENG"], "", 60, 10)
        connector.deliver({"id": "r1", "conversationID": "OTHER-1", "body": "no"})
        connector.deliver({"id": "r2", "conversationID": "ENG-1", "body": "done"})
        self.assertEqual(termite.acks[0][1], False)
        self.assertEqual(termite.acks[1], ("r2", False, "denied"))
    def test_stale_recovery_copy_is_not_acked_twice(self):
        termite = FakeTermite(); termite.queued = {"r1"}; jira = FakeJira()
        connector = channel.JiraConnector(termite, jira, ["ENG"], "", 60, 10)
        reply = {"id": "r1", "conversationID": "ENG-1", "body": "done"}
        connector.deliver(reply); connector.deliver(reply)
        self.assertEqual(jira.sent, [("ENG-1", "done")])
        self.assertEqual(termite.acks, [("r1", True)])


if __name__ == "__main__": unittest.main()
