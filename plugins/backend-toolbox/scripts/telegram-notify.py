#!/usr/bin/env python3
"""
Telegram notification hook for backend-toolbox.

Set environment variables:
    export TELEGRAM_BOT_TOKEN="your_bot_token"
    export TELEGRAM_CHAT_ID="your_chat_id"
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError

LOG_FILE = "/tmp/claude-hooks.log"
MAX_MESSAGE_LENGTH = 3500


def log(message: str) -> None:
    """Append a timestamped message to the log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")


def send_telegram_message(token: str, chat_id: str, text: str) -> None:
    """Send a message to Telegram."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": text}).encode("utf-8")
    request = Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urlopen(request) as response:
            response.read()
    except URLError as e:
        log(f"Failed to send Telegram message: {e}")


def extract_last_user_prompt(transcript_path: str) -> str:
    """Extract the last user prompt from a JSONL transcript file."""
    try:
        content = Path(transcript_path).read_text()
        last_prompt = "unknown"
        for line in content.splitlines():
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
                if entry.get("type") == "user" and "message" in entry:
                    message_content = entry["message"].get("content", "")
                    if isinstance(message_content, str):
                        last_prompt = message_content
                    elif isinstance(message_content, list):
                        # Handle array content (e.g., tool results)
                        last_prompt = str(message_content)
            except json.JSONDecodeError:
                continue
        return last_prompt
    except Exception as e:
        log(f"Failed to extract prompt from transcript: {e}")
        return "unknown"


def send_chunked_message(token: str, chat_id: str, text: str) -> None:
    """Send a message to Telegram, chunking if necessary."""
    if len(text) <= MAX_MESSAGE_LENGTH:
        send_telegram_message(token, chat_id, text)
        return

    total_chunks = (len(text) + MAX_MESSAGE_LENGTH - 1) // MAX_MESSAGE_LENGTH
    for i, start in enumerate(range(0, len(text), MAX_MESSAGE_LENGTH), 1):
        chunk = text[start : start + MAX_MESSAGE_LENGTH]
        send_telegram_message(token, chat_id, f"({i}/{total_chunks})\n{chunk}")


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        log("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID, skipping")
        sys.exit(0)

    message_type = sys.argv[1] if len(sys.argv) > 1 else "Update"

    stdin_data = sys.stdin.read()

    try:
        input_data = json.loads(stdin_data) if stdin_data.strip() else {}
    except json.JSONDecodeError:
        input_data = {}

    log("Full input metadata:")
    log(json.dumps(input_data, indent=2))

    cwd = input_data.get("cwd", "")
    project = Path(cwd).name if cwd else "unknown"
    transcript_path = input_data.get("transcript_path", "")

    if transcript_path and Path(transcript_path).is_file():
        last_prompt = extract_last_user_prompt(transcript_path)
    else:
        last_prompt = "unknown"

    header = f"Claude Code: {message_type}\nProject: {project}"
    full_text = f"{header}\nPrompt: {last_prompt}"

    send_chunked_message(token, chat_id, full_text)


if __name__ == "__main__":
    main()
