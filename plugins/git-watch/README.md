# Git Watch

Git Watch reads commits from one local Git repository you explicitly choose and
turns them into Termite Work Items. It is deliberately one-way: the manifest
requests only `channels`, the Channel advertises no reply capability, and the
connector runs only read-only `git rev-parse`, `git log`, and `git show` calls.

Copy `config.example.json` to `config.json`, set `repository` to a narrow local
checkout, and set `enabled` to true. There is no home-directory or current-
directory default. Relative paths resolve beside the connector. Environment
overrides are `TERMITE_GIT_WATCH_ENABLED`, `TERMITE_GIT_REPO`,
`TERMITE_GIT_INCLUDE_EXISTING`, `TERMITE_GIT_INTERVAL`, and
`TERMITE_GIT_MAX_COMMITS`.

By default, commits already present at launch form the baseline; only later
commits enter the Inbox. `includeExistingCommits` imports up to the configured
recent limit on first poll. Each Work Item uses the repository identity plus
immutable commit hash as its delivery id, so Termite deduplicates retries.

Git runs with fixed argv, `shell=False`, a minimal environment, five-second
timeouts, 64-KiB output bounds, exponential error backoff, and no credential
prompt. Commit message output is bounded and may be marked truncated.

Run offline tests with `python3 -m unittest discover -s .` from this directory.
