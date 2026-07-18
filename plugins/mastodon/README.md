# Mastodon Mentions

Mastodon Mentions polls the official REST API for mention notifications and
imports them as Termite Work Items. The immutable notification id is the
`deliveryID`, scoped by instance, so retries are idempotent and changing
instances cannot collide with old Channel state. The last fully ingested notification
is advanced atomically only after Termite accepts the batch. Responses and
Work Item text are bounded; HTML becomes readable plain text.
Newest-first notification bursts are paged back to the prior durable cursor;
a failed or non-advancing page leaves that cursor unchanged for safe replay.

Approved Termite replies use `POST /api/v1/statuses`, the original status as
`in_reply_to_id`, and the stable Termite reply id as Mastodon's
`Idempotency-Key`. Replies queued while offline are recovered on registration;
live delivery uses Termite's private SSE stream. Provider failures are
acknowledged as failed and are never automatically retried or marked sent.
At startup the connector verifies the token's account id and excludes that
account's own notifications, preventing posted replies from returning as new
work. It also polls queued replies before every SSE reconnection.

Copy `config.example.json` to `config.json` beside `channel.py`. Environment
variables override it: `MASTODON_BASE_URL`, `MASTODON_ACCESS_TOKEN`,
`MASTODON_POLL_SECONDS`, `MASTODON_MAX_NOTIFICATIONS`,
`MASTODON_REPLY_VISIBILITY`, `MASTODON_MAX_REPLY_CHARACTERS`,
`MASTODON_ACCOUNT`, and optionally `MASTODON_STATE_FILE`.

Create a Mastodon access token allowed to read notifications and post statuses.
Do not put it in the manifest or example file. If absent, macOS Keychain
service `termite.mastodon` is checked:

```sh
security add-generic-password -U -s termite.mastodon -a '@you@example.social' -w
```

Remote instances must use HTTPS. For a local test server only, loopback HTTP
can be explicitly enabled with `allow_insecure_local: true` or
`MASTODON_ALLOW_INSECURE_LOCAL=1`. Poll failures use bounded exponential
backoff. Replies exceeding the configured instance-size approximation fail
visibly so the user can shorten and explicitly retry them.
Authenticated API redirects are restricted to same-origin GETs; reply POST
redirects are rejected.

Run offline normalization/state/config tests with `python3 test_channel.py`.
