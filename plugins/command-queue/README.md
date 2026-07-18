# Command Queue

Command Queue is a local adapter for tools that already speak JSON. An
explicitly configured **producer** is polled for Work Items. Only after a user
reviews and sends a Termite reply is an explicitly configured **consumer** run
with that reply as one JSON object on standard input.

The connector has no command defaults and refuses to start until `config.json`
contains `"enabled": true` plus non-empty `producer` and `consumer` **argv
arrays**. Bare command strings are rejected. Commands run with `shell=False`,
a minimal environment, fixed argv, closed extra file descriptors, bounded
stdout/stderr, and configurable timeouts clamped to 60 seconds. Incoming or
reply text is never interpolated into argv or a shell. An administrator can
still explicitly configure a shell executable in an argv array; doing so grants
that configured program the shell's authority and should be avoided when a
direct executable is available.

Producer output may be one item, an item array, or `{"items": [...]}`. Each item
must have a stable provider `deliveryID` and non-empty `body`; optional fields
are `title`, `conversationID`, `replyToID`, `senderID`, `senderName`,
`createdAt`, and `projectHint`. At most 64 items and 512 KiB are accepted per
poll, with a 64-KiB body limit. Termite identity is derived from deliveryID.

The consumer receives `version`, stable reply `id`, `channel`,
`conversationID`, `replyToID`, `kind`, and `body`. It must use `id` as its
idempotency key because delivery is at least once if it succeeds and the
connector crashes before acknowledgement. Exit 0 means delivered; timeout,
non-zero exit, or excess output is acknowledged as failed for deliberate user
retry. Queued replies recover at registration and every private SSE reconnect.

Environment overrides include `TERMITE_COMMAND_QUEUE_ENABLED`,
`TERMITE_COMMAND_QUEUE_PRODUCER_JSON`, `TERMITE_COMMAND_QUEUE_CONSUMER_JSON`,
`TERMITE_COMMAND_QUEUE_INTERVAL`, both `*_TIMEOUT` variables, and
`TERMITE_COMMAND_QUEUE_MAX_ITEMS`. Command overrides must be JSON arrays.

Run offline tests with `python3 -m unittest discover -s .` from this directory.
