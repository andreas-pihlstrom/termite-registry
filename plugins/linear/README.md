# Linear Channel

Routes recently observed Linear issues from explicit team and/or project UUIDs
into Termite. By default it narrows further to issues assigned to the API-key
owner. Each issue is ingested once; approved replies create issue comments.

## Setup

1. Create a personal API key in Linear's Security & access settings. Copy model
   UUIDs with Linear's command menu: open a team/project, press Cmd-K, and use
   **Copy model UUID**.
2. Copy `config.example.json` to `config.json`. Populate `teamIds`,
   `projectIds`, or both. When both are present, an issue must match both
   allowlists. The connector refuses an unscoped configuration.
3. Store the key in macOS Keychain (recommended):

   ```sh
   security add-generic-password -U -s termite.linear -a "$USER" -w
   ```

4. Run `termite extension validate .` and `termite extension dev .`.

Overrides: `TERMITE_LINEAR_API_KEY`, comma-separated
`TERMITE_LINEAR_TEAM_IDS`, `TERMITE_LINEAR_PROJECT_IDS`,
`TERMITE_LINEAR_ASSIGNED_TO_ME_ONLY`, `TERMITE_LINEAR_ACCOUNT`,
`TERMITE_LINEAR_POLL_SECONDS` (10–3600), and
`TERMITE_LINEAR_INITIAL_LOOKBACK_SECONDS` (0–2592000).

The connector follows Linear's recommendation to filter and page a single
recently-updated issues query rather than polling individual issues. A stable
Linear issue UUID is the Termite delivery ID, so later edits do not create a
second Work Item. Poll windows overlap and Termite deduplicates observations.

Before every outbound comment, the connector re-fetches the issue scope and
rejects anything outside the configured team/project allowlists or the
`assignedToMeOnly` constraint. A stable non-secret HTML
marker is checked in the latest 100 comments to make recovery idempotent.
Descriptions are text-only; authenticated attachments are not downloaded.
Incoming text remains untrusted and never runs or sends automatically.

If `apiKey` is stored in `config.json`, run `chmod 600 config.json`; never
commit it. Personal keys act as the user, so keep the team/project scope narrow.

## Offline tests

```sh
python3 -m unittest -v test_channel.py
```
