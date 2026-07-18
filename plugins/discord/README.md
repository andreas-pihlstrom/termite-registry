# Discord Channel

Routes text messages from explicitly allowlisted Discord channels into Termite
and posts approved replies back to the source message. It uses bounded REST
polling, so it needs neither a public webhook nor a third-party WebSocket
library.

## Setup

1. Create a Discord application and bot. Give it only `View Channel`, `Read
   Message History`, and `Send Messages` in the selected channels. Enable the
   privileged **Message Content Intent** in the Developer Portal when Discord
   requires it for your app; without it, ordinary message `content` may be
   empty. This connector does not need Administrator permission.
2. Copy `config.example.json` to `config.json` and list numeric channel or
   thread IDs in `channelIds`. The connector refuses an empty allowlist.
3. Store the bot token in Keychain (recommended):

   ```sh
   security add-generic-password -U -s termite.discord -a "$USER" -w
   ```

4. Run `termite extension validate .` and `termite extension dev .`.

Environment overrides are `TERMITE_DISCORD_BOT_TOKEN`, comma-separated
`TERMITE_DISCORD_CHANNEL_IDS`, `TERMITE_DISCORD_ACCOUNT`,
`TERMITE_DISCORD_POLL_SECONDS` (2–300), and
`TERMITE_DISCORD_INITIAL_FETCH_LIMIT` (1–100).

Discord snowflakes are immutable delivery IDs. Approved messages use a stable
nonce with `enforce_nonce`, which protects provider delivery across connector
recovery. Replies suppress all mention parsing, so generated text cannot ping
roles or users unexpectedly. Attachments and embeds are not downloaded.
Incoming text remains untrusted and Termite still requires review before work
or sending.

If `botToken` is put in `config.json`, use `chmod 600 config.json`; never commit
it. Rate-limit responses are retried at most twice with a capped provider delay.

## Offline tests

```sh
python3 -m unittest -v test_channel.py
```
