import os
import io
import http.server
import threading
import urllib.error
import urllib.request
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import channel


class FakeTermite:
    def __init__(self):
        self.items, self.acks, self.queued = [], [], None
    def ingest(self, item): self.items.append(item)
    def reply_is_queued(self, reply_id): return self.queued is None or reply_id in self.queued
    def acknowledge(self, *args):
        self.acks.append(args)
        if self.queued is not None: self.queued.discard(args[0])


class FakeSlack:
    def __init__(self, messages=None, failure=None):
        self.messages, self.failure = messages or [], failure
    def history(self, channel_id, oldest): return self.messages
    def user_name(self, user_id): return "Mira"
    def send(self, reply):
        if self.failure: raise channel.ConnectorError(self.failure)


class SlackConnectorTests(unittest.TestCase):
    def test_authenticated_request_does_not_follow_cross_origin_redirect(self):
        class Target(http.server.BaseHTTPRequestHandler):
            hits = 0
            def do_GET(self):
                type(self).hits += 1
                self.send_response(200); self.end_headers(); self.wfile.write(b"{}")
            def log_message(self, *args): pass
        target = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Target)
        target_thread = threading.Thread(target=target.serve_forever, daemon=True); target_thread.start()
        location = f"http://127.0.0.1:{target.server_port}/stolen"
        class Redirect(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(302); self.send_header("Location", location); self.end_headers()
            def log_message(self, *args): pass
        source = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Redirect)
        source_thread = threading.Thread(target=source.serve_forever, daemon=True); source_thread.start()
        try:
            request = urllib.request.Request(f"http://127.0.0.1:{source.server_port}/",
                                             headers={"Authorization": "Bearer secret"})
            with self.assertRaises(urllib.error.HTTPError): channel.rejecting_opener().open(request, timeout=2)
            self.assertEqual(Target.hits, 0)
        finally:
            source.shutdown(); target.shutdown(); source.server_close(); target.server_close()

    def test_oversized_http_response_is_rejected(self):
        with mock.patch.object(channel, "MAX_HTTP_BYTES", 4):
            with self.assertRaises(channel.ConnectorError): channel.read_json(io.BytesIO(b"12345"), "test")

    def test_poll_normalizes_and_filters(self):
        termite = FakeTermite()
        slack = FakeSlack([
            {"ts": "1712345.100", "user": "U1", "text": "Ship it"},
            {"ts": "1712345.200", "user": "BOT", "bot_id": "B1", "text": "ignore"},
        ])
        connector = channel.SlackConnector(termite, slack, "C1", "team", 5, 0)
        connector.own_user_id = "SELF"
        connector.oldest = "0"
        connector.poll_once()
        self.assertEqual(len(termite.items), 1)
        self.assertEqual(termite.items[0]["deliveryID"], "slack:C1:1712345.100")
        self.assertEqual(termite.items[0]["replyToID"], "1712345.100")

    def test_failed_delivery_is_acknowledged(self):
        termite = FakeTermite()
        connector = channel.SlackConnector(termite, FakeSlack(failure="rejected"), "C1", "team", 5, 0)
        connector.deliver({"id": "r1", "conversationID": "C1", "body": "done"})
        self.assertEqual(termite.acks, [("r1", False, "rejected")])

    def test_stale_recovery_copy_is_not_sent_or_acked_twice(self):
        termite = FakeTermite(); termite.queued = {"r1"}
        slack = FakeSlack(); connector = channel.SlackConnector(termite, slack, "C1", "team", 5, 0)
        reply = {"id": "r1", "conversationID": "C1", "body": "done"}
        connector.deliver(reply); connector.deliver(reply)
        self.assertEqual(termite.acks, [("r1", True)])

    def test_environment_overrides_config(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text('{"channelId":"FILE"}')
            with mock.patch.dict(os.environ, {"TERMITE_SLACK_CHANNEL_ID": "ENV"}):
                self.assertEqual(channel.setting(channel.load_file_config(path), "channelId", "TERMITE_SLACK_CHANNEL_ID"), "ENV")


if __name__ == "__main__":
    unittest.main()
