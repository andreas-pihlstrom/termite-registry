# Telegram Channel

Routes text and caption messages from an explicit Telegram chat allowlist into
Termite using Bot API long polling. Approved replies return to the originating
message. No webhook or public server is required.

## Setup

1. Create a bot with BotFather. Add it to only the chats it should read. In a
   group, disable privacy mode only if the bot should receive ordinary group
   messages.
2. Copy `config.example.json` to `config.json` and list numeric chat IDs in
   `allowedChatIds`. The connector refuses to start without an allowlist.
3. Store the bot token in macOS Keychain (recommended):

   ```sh
   security add-generic-password -U -s termite.telegram -a "$USER" -w
   ```

4. Run `termite extension validate .` and `termite extension dev .`.

For development, `TERMITE_TELEGRAM_BOT_TOKEN` and the comma-separated
`TERMITE_TELEGRAM_ALLOWED_CHAT_IDS` override Keychain/config. Optional:
`TERMITE_TELEGRAM_ACCOUNT` and `TERMITE_TELEGRAM_LONG_POLL_SECONDS` (5–50).

Telegram update IDs are used as immutable delivery IDs. Termite therefore
deduplicates polling retries. Telegram has no client idempotency key for
`sendMessage`; a process crash after Telegram accepts a message but before the
Termite acknowledgement can duplicate an explicitly retried reply. The UI
should be treated as the authority for retrying failed delivery.

Media is not downloaded; captions are accepted as text. Incoming content is
untrusted and never executes or sends automatically. If `botToken` is placed
in `config.json`, run `chmod 600 config.json` and never commit it.

## Offline tests

```sh
python3 -m unittest -v test_channel.py
```
