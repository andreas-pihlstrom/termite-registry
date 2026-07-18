# Slack Channel

Routes new top-level text messages from one explicitly selected Slack channel
into Termite. Approved Termite replies are posted into the originating Slack
thread. It polls Slack's Web API; it does not require a public webhook.

## Setup

1. Create a Slack app and bot token with `channels:history` (public channels) or
   `groups:history` (private channels), `chat:write`, and `users:read`. Install
   the app to the workspace and invite it to the selected channel.
2. Copy `config.example.json` to `config.json`; set `channelId` to the Slack
   channel ID. `config.json` is ignored by Git.
3. Store the bot token in macOS Keychain (recommended):

   ```sh
   security add-generic-password -U -s termite.slack -a "$USER" -w
   ```

4. Validate and run with `termite extension validate .` and
   `termite extension dev .`.

For shell development, `TERMITE_SLACK_BOT_TOKEN` and
`TERMITE_SLACK_CHANNEL_ID` override the file and Keychain. Optional overrides:
`TERMITE_SLACK_ACCOUNT`, `TERMITE_SLACK_POLL_SECONDS` (2–300), and
`TERMITE_SLACK_INITIAL_LOOKBACK_SECONDS` (0–86400).

This connector ingests text only, ignores bot/subtype messages, and does not
download files or mirror thread replies. Slack message timestamps are stable
delivery IDs, so repeated polls are idempotent. Outbound messages use a stable
`client_msg_id`. Incoming Slack text remains untrusted input and is never run
or sent back without Termite's review and explicit send step.

If a token is placed in `config.json` under `botToken`, protect it with
`chmod 600 config.json`; Keychain is preferable. Never commit that file.

## Offline tests

```sh
python3 -m unittest -v test_channel.py
```
