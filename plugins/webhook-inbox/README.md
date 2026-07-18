# Webhook Inbox

Webhook Inbox turns authenticated JSON `POST`s into idempotent Termite Work
Items. It listens on loopback by default. If a single fixed callback URL is
configured, approved Termite replies are posted there and acknowledged only
after a successful HTTP response. It never executes incoming text.

## Configure

Copy `config.example.json` to `config.json` beside `channel.py`. This works for
Extensions launched from Finder. Environment variables override the file:

| JSON key | Environment | Meaning |
|---|---|---|
| `listen_host` | `WEBHOOK_LISTEN_HOST` | Bind address; default `127.0.0.1` |
| `listen_port` | `WEBHOOK_LISTEN_PORT` | Receiver port; default `8787` |
| `inbound_secret` | `WEBHOOK_SECRET` | Expected bearer token |
| `callback_url` | `WEBHOOK_REPLY_URL` | One HTTPS endpoint for approved replies |
| `callback_bearer_token` | `WEBHOOK_REPLY_TOKEN` | Optional callback bearer token |
| `allow_insecure_local_callback` | `WEBHOOK_ALLOW_INSECURE_LOCAL_CALLBACK` | Explicitly allow loopback callback HTTP |
| `max_body_bytes` | `WEBHOOK_MAX_BODY_BYTES` | Request limit, capped at 64 KiB |

When `inbound_secret` is absent, the connector also tries macOS Keychain
service `termite.webhook-inbox`. Store it with:

```sh
security add-generic-password -U -s termite.webhook-inbox -a "$USER" -w
```

No secret is included, and the connector refuses to start until one is
configured—even on loopback. Callbacks must use HTTPS. Loopback HTTP requires
the explicit local-development override. When no callback is set the Channel
truthfully advertises no reply capability.

Callback POST redirects are rejected rather than followed, so a callback
cannot move its bearer credential or approved reply to another endpoint.
Failure records contain only a bounded error category/HTTP status and never
persist a signed callback URL.

## Send an event

```sh
curl http://127.0.0.1:8787/events \
  -H 'Authorization: Bearer YOUR_SECRET' \
  -H 'Content-Type: application/json' \
  -d '{
    "deliveryID":"build-1842",
    "conversationID":"deploys",
    "senderName":"CI",
    "title":"Staging failed",
    "body":"The staging smoke test failed. Review the attached log in CI."
  }'
```

`deliveryID` is required and must be the sender's immutable event identity;
retries are deduplicated by Termite. The optional callback receives JSON with
the stable Termite reply id and an `Idempotency-Key` header. Queued replies are
recovered during registration and live replies arrive over the private SSE
stream. Failed callbacks are acknowledged as failed and require explicit user
retry in Termite.

Run offline tests with `python3 test_channel.py`.
