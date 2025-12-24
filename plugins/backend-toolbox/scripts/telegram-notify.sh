#!/bin/bash

# Telegram notification hook for backend-toolbox
# Set environment variables:
#   export TELEGRAM_BOT_TOKEN="your_bot_token"
#   export TELEGRAM_CHAT_ID="your_chat_id"

if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$TELEGRAM_CHAT_ID" ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID, skipping" >> /tmp/claude-hooks.log
  exit 0
fi

# Get message type from argument (default: "Update")
message_type="${1:-Update}"

input=$(cat)

session_id=$(echo "$input" | jq -r '.session_id // "unknown"' | cut -c1-8)
cwd=$(echo "$input" | jq -r '.cwd // ""')
project=$(basename "$cwd")

message="Claude Code: $message_type
Project: $project
Session: $session_id"

curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -H 'Content-Type: application/json' \
  -d "{\"chat_id\": \"$TELEGRAM_CHAT_ID\", \"text\": \"$message\"}" > /dev/null 2>&1

exit 0
