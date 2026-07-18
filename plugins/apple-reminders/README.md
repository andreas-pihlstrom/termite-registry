# Apple Reminders

Apple Reminders reads incomplete reminders from exact list names or list ids you
allowlist and makes them Termite Work Items. It is intentionally **read-only**:
the manifest requests only `channels`, the Channel advertises no replies, and
the fixed JXA program contains no create, modify, complete, or delete operation.

We deliberately did not map free-form Termite replies to “append note” or
“complete reminder.” Those are different irreversible intents, and AppleScript
does not provide a sufficiently strong acknowledgement/idempotency contract to
guess between them after a crash. A future connector can expose them as
separate reviewed Actions.

Copy `config.example.json` to `config.json`, set `enabled` true, and populate
`allowedListNames` and/or `allowedListIDs`. An empty allowlist refuses to start.
macOS will request Automation permission for Termite to read Reminders.

Environment overrides are `TERMITE_REMINDERS_ENABLED`,
`TERMITE_REMINDERS_LIST_NAMES_JSON`, `TERMITE_REMINDERS_LIST_IDS_JSON`,
`TERMITE_REMINDERS_INTERVAL`, and `TERMITE_REMINDERS_MAX_ITEMS`. List values
are JSON arrays. The list allowlists are passed as JSON argv to a constant JXA
program; they are never inserted into source or a shell.

The process uses fixed argv, `shell=False`, a minimal environment, a 15-second
timeout, 512-KiB output and 100-item limits, and exponential error backoff.
Large allowlisted sets are paged across polls. Stable Apple reminder ids become
stable Termite delivery identities, so retries and restarts deduplicate.

Run offline tests with `python3 -m unittest discover -s .` from this directory.
