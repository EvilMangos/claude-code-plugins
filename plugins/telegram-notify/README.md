# telegram-notify

A hook to send Telegram notifications on task finish or when user action is required

## Features

- Sends notifications when Claude finishes a task
- Sends notifications when user action is required (permission prompts, idle prompts)
- Compact message format with project name and session info
- Extracts and displays the last user prompt for context

## Installation

```bash
claude plugins add telegram-notify --marketplace evil-mangos-market
```

## Configuration

Set these environment variables before starting Claude Code:

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
```

### Getting Your Bot Token

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the prompts
3. Copy the API token provided

### Getting Your Chat ID

1. Message [@userinfobot](https://t.me/userinfobot) on Telegram
2. It will reply with your chat ID

## Notification Types

| Event | Trigger | Message |
|-------|---------|---------|
| Task Complete | Claude stops working | "Finished" |
| Action Required | Permission or idle prompt | "Action Required" |

## Message Format

```
🤖 Finished
📁 my-project · a1b2c3d4
💬 fix the login bug
```

- First line: Event type
- Second line: Project name and session ID
- Third line: Last user prompt (if available)

## License

MIT
