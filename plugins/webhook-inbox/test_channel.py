import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

SPEC = importlib.util.spec_from_file_location("webhook_channel", Path(__file__).with_name("channel.py"))
channel = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(channel)


class WebhookTests(unittest.TestCase):
    def test_stable_normalization(self):
        first = channel.normalize_event({"deliveryID": "evt-42", "body": "build it"})
        again = channel.normalize_event({"deliveryID": "evt-42", "body": "build it"})
        self.assertEqual(first, again)
        self.assertEqual(first["conversationID"], "evt-42")

    def test_requires_provider_delivery_id(self):
        with self.assertRaisesRegex(ValueError, "deliveryID"):
            channel.normalize_event({"body": "missing identity"})

    def test_environment_overrides_config(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory, "config.json")
            config.write_text(json.dumps({"listen_port": 1000}))
            with mock.patch.object(channel, "PLUGIN_DIR", Path(directory)), mock.patch.dict(
                os.environ, {"WEBHOOK_LISTEN_PORT": "2345"}, clear=False
            ):
                with mock.patch.object(channel, "_keychain", return_value="secret"):
                    self.assertEqual(channel.load_config()["listen_port"], 2345)

    def test_secret_is_required_even_on_loopback(self):
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(
            channel, "PLUGIN_DIR", Path(directory)
        ), mock.patch.object(channel, "_keychain", return_value=""):
            with self.assertRaisesRegex(ValueError, "WEBHOOK_SECRET"):
                channel.load_config()

    def test_long_delivery_ids_remain_distinct_after_bounding(self):
        prefix = "x" * 600
        first = channel.normalize_event({"deliveryID": prefix + "a", "body": "one"})
        second = channel.normalize_event({"deliveryID": prefix + "b", "body": "two"})
        self.assertLessEqual(len(first["deliveryID"].encode()), 512)
        self.assertNotEqual(first["deliveryID"], second["deliveryID"])

    def test_callback_rejects_cross_origin_and_post_redirects(self):
        handler = channel.SameOriginRedirect()
        request = channel.urllib.request.Request("https://one.test/hook", data=b"{}", method="POST")
        with self.assertRaises(channel.urllib.error.HTTPError):
            handler.redirect_request(request, None, 307, "redirect", {}, "https://one.test/new")
        get = channel.urllib.request.Request("https://one.test/hook")
        with self.assertRaises(channel.urllib.error.HTTPError):
            handler.redirect_request(get, None, 302, "redirect", {}, "https://two.test/new")

    def test_recovery_only_delivers_owned_queued_replies(self):
        client = mock.Mock()
        client.request.return_value = {"replies": [
            {"id": "ours", "channel": channel.CHANNEL_ID},
            {"id": "other", "channel": "dev.other"},
        ]}
        with mock.patch.object(channel, "deliver_reply") as deliver:
            channel.recover_pending(client, {})
        deliver.assert_called_once_with(client, {}, {"id": "ours", "channel": channel.CHANNEL_ID})

    def test_callback_errors_do_not_persist_secret_urls(self):
        error = channel.urllib.error.HTTPError(
            "https://callback.test/hook?secret=do-not-store", 500, "failed", {}, None
        )
        self.assertEqual(channel.provider_error(error), "HTTP 500")
        self.assertNotIn("secret", channel.provider_error(error))

    def test_success_ack_failure_is_not_relabelled_provider_failure(self):
        client = mock.Mock()
        client.request.side_effect = RuntimeError("host temporarily unavailable")
        response = mock.MagicMock(status=204)
        context = mock.MagicMock()
        context.__enter__.return_value = response
        reply = {"id": "r1", "conversationID": "c", "body": "done"}
        with mock.patch.object(channel.HTTP, "open", return_value=context):
            with self.assertRaisesRegex(RuntimeError, "host temporarily"):
                channel.deliver_reply(client, {"callback_url": "https://callback.test/hook", "callback_bearer_token": ""}, reply)
        client.request.assert_called_once_with("/v1/channel-replies/r1/ack", {"delivered": True})


if __name__ == "__main__":
    unittest.main()
