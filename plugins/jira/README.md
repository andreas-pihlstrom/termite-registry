# Jira Cloud Channel

Routes Jira Cloud issues and their latest comments from explicit project keys
into Termite. Approved replies are posted as Jira comments. This connector is
for `*.atlassian.net` Jira Cloud sites only; it deliberately rejects custom
hosts, Jira Data Center, URL paths, and unscoped project access.

## Setup

1. Create an Atlassian API token for an account with Browse Projects, Add
   Comments, and issue-security access only where needed.
2. Copy `config.example.json` to `config.json`; set the exact HTTPS Jira Cloud
   origin, account email, and `projectKeys`. The connector refuses an empty or
   syntactically invalid project allowlist.
3. Store the API token in Keychain (recommended):

   ```sh
   security add-generic-password -U -s termite.jira -a "$USER" -w
   ```

4. Run `termite extension validate .` and `termite extension dev .`.

Overrides: `TERMITE_JIRA_API_TOKEN`, `TERMITE_JIRA_EMAIL`,
`TERMITE_JIRA_BASE_URL`, comma-separated `TERMITE_JIRA_PROJECT_KEYS`,
`TERMITE_JIRA_ACCOUNT`, `TERMITE_JIRA_POLL_SECONDS` (30–3600), and
`TERMITE_JIRA_INITIAL_LOOKBACK_SECONDS` (0–2592000).

The connector uses Jira's current enhanced JQL search endpoint, a five-minute
overlap after each successful poll, and immutable Jira issue/comment database
IDs for Termite deduplication. Each observed issue becomes one Work Item;
edits do not create another. For each recently changed issue it pages comments
inside the overlap window, ignores self/app-authored comments, and fails clearly
if more than 400 recent comments would otherwise be dropped. A poll is capped
at 200 changed issues; narrow the project list or poll more often if either
boundary is hit.

Jira Cloud does not document an idempotency key for creating comments. A crash
after Jira accepts a comment but before Termite records the acknowledgement can
therefore duplicate a user-approved retry. Check the Jira issue before retrying
an ambiguous failure. ADF descriptions/comments are flattened to bounded text;
attachments are not downloaded. Incoming content is untrusted and never runs
or sends automatically.

If `apiToken` is stored in `config.json`, run `chmod 600 config.json`; never
commit it. Keychain is preferable.

## Offline tests

```sh
python3 -m unittest -v test_channel.py
```
