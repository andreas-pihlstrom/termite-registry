# Clipboard Inbox

Clipboard Inbox turns **changes** to the macOS text clipboard into Work Items.
It uses `/usr/bin/pbpaste` and, when separately enabled, sends a reviewed reply
with `/usr/bin/pbcopy`. It has no clipboard history and does not upload data.

This connector intentionally refuses to start until `config.json` contains both
`"enabled": true` and `"pollClipboard": true`. Copy `config.example.json` to
begin. The clipboard already present at startup is only a baseline unless
`includeCurrentClipboard` is also enabled. Polling is bounded to 64 KiB and
never faster than twice per second.

`writeApprovedReplies` is a second opt-in. When false, the registered Channel
does not advertise replies and never calls `pbcopy`. When true, only a reply the
user explicitly sends from Termite's private outbox reaches `pbcopy`. Text the
connector writes is remembered and suppressed from the inbox.

Environment overrides are `TERMITE_CLIPBOARD_ENABLED`,
`TERMITE_CLIPBOARD_POLL`, `TERMITE_CLIPBOARD_WRITE_REPLIES`,
`TERMITE_CLIPBOARD_INCLUDE_CURRENT`, and `TERMITE_CLIPBOARD_INTERVAL`.
Subprocesses use fixed argv, no shell, a minimal environment, three-second
timeouts, and bounded output. Clipboard hashes provide idempotent Work Item
identities. Failed outbound writes are acknowledged as failed; queued replies
recover at registration and on private event-stream reconnect.

Run offline tests with `python3 -m unittest discover -s .` from this directory.
