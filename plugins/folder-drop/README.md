# Folder Drop

Folder Drop watches one directory you choose. Every new or changed direct child
file becomes a Termite Work Item. A reply leaves Termite only after you review
and send it; the connector writes that approved reply as a mode-`0600` JSON file
in a separate outbox. It never executes file contents, follows symlinks, watches
recursively, or deletes/moves input.

## Configure

Copy `config.example.json` to `config.json`, choose narrow inbox and outbox
directories, and set `enabled` to `true`. Relative paths resolve next to this
connector. Nothing is watched until this opt-in exists. Environment overrides
are `TERMITE_FOLDER_DROP_ENABLED`, `TERMITE_FOLDER_DROP_INBOX`,
`TERMITE_FOLDER_DROP_OUTBOX`, and `TERMITE_FOLDER_DROP_INTERVAL`.

Plain UTF-8 files use their filename as the title. A `.json` file may contain
`body` and optional `title`, `conversationID`, `replyToID`, `senderID`,
`senderName`, or `projectHint`. File and body limits are 64 KiB. Identity is a
SHA-256 of filename plus content, so retries deduplicate and a changed file is
new work.

Approved replies are `reply-*.json` files with stable names based on the Termite
reply id. Existing files make crash recovery idempotent. Delivery failures are
acknowledged as failed; queued replies are recovered at registration and before
each private event-stream reconnect.

Run offline tests with `python3 -m unittest discover -s .` from this directory.
