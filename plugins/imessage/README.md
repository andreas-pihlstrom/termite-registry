# iMessage

This macOS Channel reads **only allowlisted incoming text messages** from the
local Messages database and routes them into Termite. It ignores messages sent
by you, does not fetch attachments or attributed-body archives, does not mirror
history by default, and never connects to an external service.

## Required permissions and configuration

1. Give the Termite app Full Disk Access in **System Settings → Privacy &
   Security → Full Disk Access** so its launched connector can open
   `~/Library/Messages/chat.db`. Do not copy or loosen permissions on the
   database.
2. Copy `config.example.json` to sibling `config.json` and set `enabled` true.
3. Add exact identifiers to `allowedHandles` and/or `allowedChatGUIDs`. The
   connector refuses to run with an empty allowlist. You can find chat GUIDs by
   inspecting your own database; treat handles and GUIDs as private data.

Environment overrides are `TERMITE_IMESSAGE_ENABLED`,
`TERMITE_IMESSAGE_DATABASE`, `TERMITE_IMESSAGE_HANDLES_JSON`,
`TERMITE_IMESSAGE_CHATS_JSON`, `TERMITE_IMESSAGE_SEND_REPLIES`,
`TERMITE_IMESSAGE_INCLUDE_EXISTING`, `TERMITE_IMESSAGE_INTERVAL`, and
`TERMITE_IMESSAGE_MAX_MESSAGES`. List overrides must be JSON arrays.

Database access is SQLite read-only, query-only, allowlist-filtered, time-
bounded, row-bounded, and body-bounded to 64 KiB. Immutable Messages GUIDs are
the delivery identity, so provider retries deduplicate. Existing history is a
baseline unless `includeExistingMessages` is explicitly enabled.

## Approved replies

`sendApprovedReplies` is a separate opt-in. When false, the Channel advertises
no reply support and does not open the event stream. When true, only a reply
the user explicitly sends from Termite is passed to Messages through
`/usr/bin/osascript`. The AppleScript source is constant; allowlisted target and
untrusted body are separate argv values, never source interpolation or a shell.
macOS will also ask for Automation permission to control Messages.

The target is rechecked against the current allowlist for every delivery.
Queued replies recover after restart; send errors are acknowledged as failed.
Apple Events delivery is at least once across a crash, so confirm ambiguous
failures before retrying.

Run offline tests with `python3 -m unittest discover -s .` from this directory.
