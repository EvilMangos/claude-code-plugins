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
from html import escape
from pathlib import Path
from typing import Any, Optional
from urllib.error import URLError
from urllib.request import Request, urlopen

LOG_FILE = "/tmp/claude-hooks.log"
MAX_MESSAGE_LENGTH = 3500


def log(message: str) -> None:
    """Append a timestamped message to the log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def send_telegram_message(token: str, chat_id: str, text: str) -> None:
    """Send a message to Telegram."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps(
        {"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
        ensure_ascii=False,
    ).encode("utf-8")
    request = Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urlopen(request) as response:
            response.read()
    except URLError as e:
        log(f"Failed to send Telegram message: {e}")


def _extract_human_text(content: Any) -> Optional[str]:
    """
    Extract human-entered text from Claude Code transcript message.content.
    Ignores tool payloads like {"type":"tool_result", ...}.
    """
    if content is None:
        return None

    if isinstance(content, str):
        text = content.strip()
        return text or None

    if isinstance(content, dict):
        if content.get("type") in {"tool_result", "tool_use"}:
            return None
        t = content.get("text")
        if isinstance(t, str) and t.strip():
            return t.strip()
        return None

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                if item.strip():
                    parts.append(item.strip())
                continue

            if not isinstance(item, dict):
                continue

            item_type = item.get("type")
            if item_type in {"tool_result", "tool_use"}:
                continue

            # Common shapes: {"type":"text","text":"..."} / {"type":"input_text","text":"..."}
            if item_type in {"text", "input_text"}:
                t = item.get("text")
                if isinstance(t, str) and t.strip():
                    parts.append(t.strip())
                continue

            # Fallback: if it has "text" and isn't a tool payload, take it
            t = item.get("text")
            if isinstance(t, str) and t.strip():
                parts.append(t.strip())

        combined = "\n".join(parts).strip()
        return combined or None

    return None


def extract_last_user_prompt(transcript_path: str) -> str:
    """Extract the last *human* user prompt from a JSONL transcript file."""
    try:
        last_prompt: Optional[str] = None

        with Path(transcript_path).open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Only consider user entries
                if entry.get("type") != "user":
                    continue

                # Prefer external user messages (tool results are often also logged as "user")
                user_type = entry.get("userType")
                if user_type not in (None, "external"):
                    continue

                msg = entry.get("message") or {}
                if msg.get("role") != "user":
                    continue

                candidate = _extract_human_text(msg.get("content"))
                if candidate:
                    last_prompt = candidate

        return last_prompt or "unknown"

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
    log(json.dumps(input_data, indent=2, ensure_ascii=False))

    cwd = input_data.get("cwd", "")
    project = Path(cwd).name if cwd else "unknown"
    transcript_path = input_data.get("transcript_path", "")

    if transcript_path and Path(transcript_path).is_file():
        last_prompt = extract_last_user_prompt(transcript_path)
    else:
        last_prompt = "unknown"

    # Escape user-supplied text because Telegram parse_mode=HTML
    header = f"<b>Claude Code:</b> {escape(message_type)}\n<b>Project:</b> {escape(project)}"
    full_text = f"{header}\n<b>Prompt:</b> {escape(last_prompt)}"

    send_chunked_message(token, chat_id, full_text)


if __name__ == "__main__":
    main()
