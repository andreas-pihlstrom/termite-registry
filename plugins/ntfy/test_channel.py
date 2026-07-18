import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

SPEC = importlib.util.spec_from_file_location("ntfy_channel", Path(__file__).with_name("channel.py"))
channel = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(channel)


class NtfyTests(unittest.TestCase):
    def test_message_identity_and_allowlist(self):
        value = {"event": "message", "id": "abc123", "time": 1700000000,
                 "topic": "alerts", "title": "Build", "message": "Failed"}
        first = channel.work_item(value, "https://ntfy.example", {"alerts"})
        again = channel.work_item(value, "https://ntfy.example", {"alerts"})
        self.assertEqual(first, again)
        self.assertIn("abc123", first["deliveryID"])
        with self.assertRaisesRegex(ValueError, "allowlisted"):
            channel.work_item(value, "https://ntfy.example", {"other"})

    def test_state_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory, "ntfy.json"))
            channel.save_since(path, "last-one")
            self.assertEqual(channel.load_since(path, "10m"), "last-one")

    def test_remote_http_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, "config.json").write_text(json.dumps({
                "server_url": "http://ntfy.test", "topics": ["alerts"]
            }))
            with mock.patch.object(channel, "PLUGIN_DIR", Path(directory)), mock.patch.object(channel, "keychain", return_value=""):
                with self.assertRaisesRegex(ValueError, "HTTPS"):
                    channel.load_config()

    def test_bad_provider_timestamp_does_not_poison_poll_batch(self):
        value = {"event": "message", "id": "abc", "time": 1e100,
                 "topic": "alerts", "message": "still ingest me"}
        item = channel.work_item(value, "https://ntfy.example", {"alerts"})
        self.assertNotIn("createdAt", item)

    def test_authenticated_redirects_cannot_change_origin(self):
        handler = channel.SameOriginRedirect()
        request = channel.urllib.request.Request("https://ntfy.test/alerts/json")
        with self.assertRaises(channel.urllib.error.HTTPError):
            handler.redirect_request(request, None, 302, "redirect", {}, "https://attacker.test/steal")

    def test_recovery_only_delivers_owned_queued_replies(self):
        client = mock.Mock()
        client.request.return_value = {"replies": [
            {"id": "ours", "channel": channel.CHANNEL_ID},
            {"id": "other", "channel": "dev.other"},
        ]}
        api = mock.Mock()
        with mock.patch.object(channel, "deliver") as deliver:
            channel.recover_pending(client, api)
        deliver.assert_called_once_with(client, api, {"id": "ours", "channel": channel.CHANNEL_ID})

    def test_success_ack_failure_is_not_relabelled_provider_failure(self):
        client = mock.Mock()
        client.request.side_effect = RuntimeError("host temporarily unavailable")
        api = mock.Mock()
        with self.assertRaisesRegex(RuntimeError, "host temporarily"):
            channel.deliver(client, api, {"id": "r1"})
        client.request.assert_called_once_with("/v1/channel-replies/r1/ack", {"delivered": True})


if __name__ == "__main__":
    unittest.main()
