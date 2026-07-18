# GitHub Issues Channel

Turns each open issue into a Work Item when first observed, and routes new issue
comments from an explicit
repository allowlist into Termite Work Items. Approved replies become issue
comments in the originating repository. Pull requests are deliberately ignored.

## Setup

1. Create a fine-grained GitHub token restricted to the selected repositories,
   with **Metadata: read** and **Issues: read and write**. No Contents or
   Administration permission is needed.
2. Copy `config.example.json` to `config.json`. Set `repositories` explicitly;
   the connector refuses to start without an allowlist. Optional `projectHints`
   can map an allowlisted repository to a local working directory.
3. Store the token in Keychain (recommended):

   ```sh
   security add-generic-password -U -s termite.github-issues -a "$USER" -w
   ```

4. Run `termite extension validate .` and `termite extension dev .`.

Environment overrides: `TERMITE_GITHUB_TOKEN`, comma-separated
`TERMITE_GITHUB_REPOSITORIES`, `TERMITE_GITHUB_ACCOUNT`,
`TERMITE_GITHUB_POLL_SECONDS` (10–3600),
`TERMITE_GITHUB_INITIAL_LOOKBACK_SECONDS` (0–2592000),
`TERMITE_GITHUB_INCLUDE_ISSUES`, and `TERMITE_GITHUB_INCLUDE_COMMENTS`.

GitHub database IDs are immutable Termite delivery IDs. Polls overlap by two
seconds and Termite deduplicates repeated provider objects. Self-authored and
bot-authored issues/comments are ignored. Outbound comments
contain a non-secret stable HTML marker; the connector searches the latest 300
comments before posting, reducing duplicates during queued-reply recovery.
GitHub does not provide a documented idempotency key for issue comments, so an
extremely active issue or a crash in the provider/ack gap can still require the
user to check before explicitly retrying.

Only allowlisted repositories can receive replies. Issue text is untrusted,
attachments are not downloaded, and nothing executes or sends without
Termite's review. If `token` is stored in `config.json`, use `chmod 600` and
never commit the file.

## Offline tests

```sh
python3 -m unittest -v test_channel.py
```
