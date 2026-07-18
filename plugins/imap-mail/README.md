# IMAP Mail

IMAP Mail polls one mailbox over TLS and imports recent messages as Work Items.
Immutable IMAP identity is the tuple of server, account, mailbox, UIDVALIDITY,
and UID, hashed into `deliveryID`; repeated polls are therefore idempotent. The
mailbox is opened read-only. Attachments and HTML are not imported, message
downloads are capped at 512 KiB, and Work Item bodies at 64 KiB.
Messages whose sender exactly matches the configured IMAP, SMTP, or From
address are ignored to keep sent-message copies from becoming reply echoes.
Provider aliases cannot be inferred automatically and should be filtered by a
dedicated inbox rule when they also deliver sent copies.

When SMTP is configured, the Channel advertises `reply` and sends only replies
the user explicitly approved in Termite. Without SMTP it truthfully advertises
no reply capability. Queued replies are recovered at registration and live
replies use Termite's private SSE stream. A stable `Message-ID` derived from the
Termite reply id is used to help downstream deduplication.

Copy `config.example.json` to `config.json` beside `channel.py`; environment
variables override it. Main variables are `IMAP_HOST`, `IMAP_PORT`,
`IMAP_USERNAME`, `IMAP_PASSWORD`, `IMAP_MAILBOX`, `IMAP_SEARCH` (`ALL` or
`UNSEEN`), `IMAP_POLL_SECONDS`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_MODE` (`ssl` or
`starttls`), `SMTP_USERNAME`, `SMTP_PASSWORD`, and `SMTP_FROM`.

If passwords are absent, the connector checks these macOS Keychain services:

```sh
security add-generic-password -U -s termite.imap-mail -a you@example.com -w
security add-generic-password -U -s termite.imap-mail.smtp -a you@example.com -w
```

No credentials are bundled. IMAP always uses certificate-verified TLS. SMTP
uses certificate-verified implicit TLS or STARTTLS. Plain SMTP exists solely
for explicit loopback testing with `allow_insecure_local: true`; it is rejected
for remote hosts. Provider errors are acknowledged as failed, never silently
marked delivered, and retry remains an explicit Termite user action.
After an SSE disconnect the connector polls Termite's queued-reply endpoint
before reconnecting, closing the missed-event recovery gap.

Run offline MIME/config tests with `python3 test_channel.py`.
