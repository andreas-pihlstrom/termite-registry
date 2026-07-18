# ntfy Topics

ntfy Topics polls up to 16 explicitly allowlisted topics and turns provider
`message` events into Termite Work Items. Each ntfy message id, scoped to the
configured server, becomes an immutable delivery identity. Poll downloads are
capped at 2 MiB and 500 messages; the last id advances atomically only after
Termite accepts every returned message.

Replies are disabled unless one fixed `reply_topic` is configured. Approved
Termite replies then publish only to that topic—never to an inbound topic taken
from untrusted message data. It must differ from every subscribed topic to
prevent reply feedback loops. Queued replies recover on registration and live
replies arrive through Termite's private SSE stream. Without `reply_topic`, the
Channel truthfully advertises no reply capability.

Copy `config.example.json` to `config.json`. Environment variables override it:
`NTFY_SERVER_URL`, `NTFY_TOPICS` (comma/newline separated),
`NTFY_ACCESS_TOKEN`, `NTFY_POLL_SECONDS`, `NTFY_INITIAL_SINCE`,
`NTFY_MAX_MESSAGES`, `NTFY_REPLY_TOPIC`, `NTFY_MAX_PUBLISH_BYTES`,
`NTFY_ACCOUNT`, and `NTFY_STATE_FILE`.

Public topics need no credential. If a token is absent, macOS Keychain service
`termite.ntfy` is checked; no credential is bundled:

```sh
security add-generic-password -U -s termite.ntfy -a ntfy-account -w
```

Servers must use HTTPS. Loopback HTTP requires the explicit
`allow_insecure_local` development override. ntfy does not offer an
idempotency-key contract for ordinary publishes: a crash after provider
acceptance but before Termite acknowledgement can duplicate a reply. The
connector includes `X-Termite-Reply-ID` for observability but does not claim the
server deduplicates it. Failed delivery requires explicit user retry.
Authenticated redirects are restricted to same-origin GETs, publish redirects
are rejected, and every SSE reconnect first polls Termite for missed queued
replies.

Run offline identity/state/config tests with `python3 test_channel.py`.
