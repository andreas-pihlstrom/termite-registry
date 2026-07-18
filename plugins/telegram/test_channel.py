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


class FakeTelegram:
    def __init__(self, updates=None, error=None): self.value, self.error = updates or [], error
    def updates(self, offset): return self.value
    def send(self, reply):
        if self.error: raise channel.ConnectorError(self.error)


class TelegramTests(unittest.TestCase):
    def test_oversized_http_response_is_rejected(self):
        with mock.patch.object(channel, "MAX_HTTP_BYTES", 4):
            with self.assertRaises(channel.ConnectorError): channel.read_json(io.BytesIO(b"12345"), "test")

    def test_requires_explicit_allowlist(self):
        with self.assertRaises(channel.ConnectorError): channel.parse_allowed("")
        self.assertEqual(channel.parse_allowed("123,-456"), {"123", "-456"})
    def test_only_allowlisted_human_text_is_ingested(self):
        updates = [
            {"update_id": 10, "message": {"message_id": 4, "date": 1700000000,
                "chat": {"id": -7, "title": "Ops"}, "from": {"id": 2, "first_name": "Mira"}, "text": "Check deploy"}},
            {"update_id": 11, "message": {"message_id": 5, "date": 1700000001,
                "chat": {"id": -8}, "from": {"id": 3}, "text": "not allowed"}},
        ]
        termite = FakeTermite(); connector = channel.TelegramConnector(termite, FakeTelegram(updates), {"-7"})
        connector.poll_once()
        self.assertEqual(len(termite.items), 1)
        self.assertEqual(termite.items[0]["deliveryID"], "telegram:10")
        self.assertEqual(connector.offset, 12)
    def test_provider_failure_is_acknowledged(self):
        termite = FakeTermite(); connector = channel.TelegramConnector(termite, FakeTelegram(error="denied"), {"-7"})
        connector.deliver({"id": "r1", "conversationID": "-7", "body": "done"})
        self.assertEqual(termite.acks, [("r1", False, "denied")])
    def test_stale_recovery_copy_is_not_acked_twice(self):
        termite = FakeTermite(); termite.queued = {"r1"}
        connector = channel.TelegramConnector(termite, FakeTelegram(), {"-7"})
        reply = {"id": "r1", "conversationID": "-7", "body": "done"}
        connector.deliver(reply); connector.deliver(reply)
        self.assertEqual(termite.acks, [("r1", True)])


if __name__ == "__main__": unittest.main()
