# RSS and Atom Feed

This read-only Channel polls up to 16 RSS 2.0 or Atom feeds and turns recent
entries into Work Items. It uses each feed's `guid`/Atom `id` (or link, then a
content hash) to make a stable delivery identity, so polling and provider
retries do not duplicate work. HTML is reduced to readable text and links are
preserved. Downloads are capped at 2 MiB and entries at 100 per feed.

Copy `config.example.json` to `config.json` beside the script. Environment
variables override it, which is useful when launching from a shell:

| JSON key | Environment | Meaning |
|---|---|---|
| `feed_urls` | `RSS_FEED_URLS` | JSON list or comma/newline-separated URLs |
| `poll_seconds` | `RSS_POLL_SECONDS` | Poll interval, 30–86400 seconds |
| `max_entries_per_feed` | `RSS_MAX_ENTRIES` | Recent items, 1–100 |
| `request_timeout` | `RSS_REQUEST_TIMEOUT` | Per-request timeout, 5–120 seconds |
| `bearer_token` | `RSS_BEARER_TOKEN` | Optional token for private feeds |
| `allow_insecure_local` | `RSS_ALLOW_INSECURE_LOCAL` | Explicit loopback HTTP development override |

If the bearer token is absent, macOS Keychain service `termite.rss-feed` is
checked. No credential is bundled:

```sh
security add-generic-password -U -s termite.rss-feed -a "$USER" -w
```

Feeds must use HTTPS. Loopback HTTP is permitted only with the explicit local
development override. Conditional `ETag` and `Last-Modified` requests reduce
work during a run; host-side delivery deduplication remains the durable
correctness layer. Failures back off without advancing or losing items.
Redirects are accepted only within the original HTTPS origin, so private-feed
credentials cannot be redirected to another host. Signed URL queries are not
printed in failure logs.

This Channel intentionally advertises an empty `replyCapabilities` array:
feeds have no reply operation. Run offline parser/config tests with
`python3 test_channel.py`.
