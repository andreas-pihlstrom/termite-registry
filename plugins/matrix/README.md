# Matrix Rooms

Matrix Rooms syncs human `m.text` and `m.emote` messages from an explicit room
ID allowlist into Termite. It ignores unlisted rooms, notices, edits/media, and
the required `own_user_id`, preventing approved replies from returning as new
work. Matrix `event_id` is used directly as the immutable
provider `deliveryID`. Sync responses are capped at 4 MiB and timelines at 100
events; the `next_batch` token advances atomically only after Termite accepts
all eligible events.

Approved replies use the original room and event, but only if the room remains
allowlisted. A hash of the stable Termite reply id is the Matrix transaction
id, making repeated `PUT /send` attempts idempotent. Queued replies recover on
registration and live replies arrive over Termite's private SSE stream.

Copy `config.example.json` to `config.json`. Environment variables override it:
`MATRIX_HOMESERVER`, `MATRIX_ACCESS_TOKEN`, `MATRIX_ROOM_IDS` (comma/newline
separated), required `MATRIX_OWN_USER_ID`, `MATRIX_SYNC_TIMEOUT_SECONDS`,
`MATRIX_TIMELINE_LIMIT`, `MATRIX_ACCOUNT`, and `MATRIX_STATE_FILE`.
The configured own user is verified against Matrix `account/whoami` at startup;
a mismatch stops the connector instead of risking reply echoes.

No credential is bundled. If the token is absent, macOS Keychain service
`termite.matrix` is checked:

```sh
security add-generic-password -U -s termite.matrix -a '@you:example.com' -w
```

The homeserver must use HTTPS. Loopback HTTP requires the explicit
`allow_insecure_local` development override. Incoming text remains untrusted
work context and is never executed. Sync and SSE failures use bounded backoff;
delivery failures are acknowledged as failed for explicit user retry.
Authenticated redirects are restricted to same-origin GETs, reply redirects
are rejected, and every SSE reconnect first polls for queued replies that may
have been missed during the outage.

Run offline allowlist/state/config tests with `python3 test_channel.py`.
