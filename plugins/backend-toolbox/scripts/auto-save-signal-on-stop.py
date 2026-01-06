#!/usr/bin/env python3
"""
SubagentStop hook: Auto-save signal if agent forgot to save it.

This hook runs when a backend-toolbox agent completes. It checks if the agent
saved its signal file. If not, it extracts context from the original prompt
and saves a signal based on the agent's transcript.
"""
import json
import os
import re
import sys
from pathlib import Path


def get_task_reports_base() -> Path:
    """Get base directory for task reports (matches _base-dir.sh logic)."""
    # Check for explicit override (matches bash script: TASK_REPORTS_DIR)
    override = os.environ.get("TASK_REPORTS_DIR")
    if override:
        return Path(override)

    # Find git root or use cwd
    cwd = Path.cwd()
    current = cwd
    while current != current.parent:
        if (current / ".git").exists():
            return current / ".task-reports"
        current = current.parent

    return cwd / ".task-reports"


def parse_workflow_context(prompt: str) -> dict:
    """Extract TASK_ID and reportType from the original prompt."""
    result = {"task_id": None, "report_type": None}

    # Extract TASK_ID
    task_match = re.search(r'TASK_ID:\s*[`"]?(\S+?)[`"]?\s', prompt)
    if task_match:
        result["task_id"] = task_match.group(1).strip('`"')

    # Extract Output reportType - try multiple formats
    # Format 1: ## Output\nreportType: xxx
    output_match = re.search(r'##\s*Output\s*\n\s*reportType:\s*(\S+)', prompt)
    if output_match:
        result["report_type"] = output_match.group(1)
    else:
        # Format 2: reportType: xxx (anywhere in prompt)
        inline_match = re.search(r'reportType:\s*(\S+)', prompt)
        if inline_match:
            result["report_type"] = inline_match.group(1)

    return result


def extract_markdown_sections(transcript: str) -> str:
    """
    Extract all markdown sections (## headings and their content) from transcript.
    Returns the markdown content suitable for saving as a report.
    """
    if not transcript:
        return ""

    # Find all lines that are markdown headings or content between them
    lines = transcript.split('\n')
    markdown_lines = []
    in_section = False

    for line in lines:
        # Check if this is a ## heading (but not ### or ####)
        if re.match(r'^##\s+[^#]', line):
            in_section = True
            markdown_lines.append(line)
        elif in_section:
            # If we hit a new # heading at any level, we're still in markdown
            if line.startswith('#'):
                markdown_lines.append(line)
            # Blank lines are part of markdown
            elif line.strip() == '':
                markdown_lines.append(line)
            # Any other content continues the section
            else:
                markdown_lines.append(line)

    content = '\n'.join(markdown_lines).strip()

    # If no markdown sections found, return the full transcript with a warning header
    if not content:
        return f"## Agent Output\n\n{transcript}\n\n> Note: No structured markdown sections found. Full transcript included."

    return content


def save_report(task_id: str, report_type: str, content: str) -> bool:
    """Save a report file with markdown content."""
    base = get_task_reports_base()
    reports_dir = base / task_id / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    report_file = reports_dir / f"{report_type}.md"

    try:
        with open(report_file, 'w') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Failed to save report: {e}", file=sys.stderr)
        return False


def parse_status_from_transcript(transcript: str) -> tuple[str, str]:
    """
    Parse explicit STATUS: PASSED/FAILED from transcript.
    Falls back to heuristic analysis if no explicit status found.
    Returns (status, summary).
    """
    # First, look for explicit STATUS declaration
    status_match = re.search(r'STATUS:\s*(PASSED|FAILED)', transcript, re.IGNORECASE)
    if status_match:
        status = status_match.group(1).lower()

        # Try to extract a summary from the context around the status
        # Look for text on the same line or the line before
        lines = transcript.split('\n')
        for i, line in enumerate(lines):
            if 'STATUS:' in line.upper():
                # Check if there's text after STATUS on the same line
                after_status = line.split(':', 1)[-1].replace(status.upper(), '').strip()
                if after_status and len(after_status) > 10:
                    return status, after_status[:200]
                # Check previous line for summary
                if i > 0 and lines[i-1].strip():
                    return status, lines[i-1].strip()[:200]
                break

        # Default summary based on status
        if status == "passed":
            return status, "Agent completed successfully"
        else:
            return status, "Agent reported failure"

    # Fallback to heuristic analysis
    transcript_lower = transcript.lower()

    failure_indicators = [
        "error:", "failed:", "exception:", "traceback:",
        "could not", "unable to", "cannot find", "not found",
        "assertion error", "test failed", "tests failed"
    ]

    for indicator in failure_indicators:
        if indicator in transcript_lower:
            lines = transcript.split('\n')
            for line in lines:
                if indicator.replace(":", "") in line.lower():
                    return "failed", f"ERROR: {line[:100].strip()}"
            return "failed", "ERROR: Agent encountered issues (auto-detected)"

    # Default to passed if no failures detected
    return "passed", "Agent completed (no explicit status found, assuming success)"


def save_signal(task_id: str, report_type: str, status: str, summary: str) -> bool:
    """Save a signal file."""
    base = get_task_reports_base()
    signals_dir = base / task_id / "signals"
    signals_dir.mkdir(parents=True, exist_ok=True)

    signal_file = signals_dir / f"{report_type}.json"

    signal_data = {
        "taskId": task_id,
        "signalType": report_type,
        "status": status,
        "summary": summary,
        "autoSaved": True,
        "savedBy": "SubagentStop hook"
    }

    try:
        with open(signal_file, 'w') as f:
            json.dump(signal_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Failed to save signal: {e}", file=sys.stderr)
        return False


def extract_text_from_content(content) -> str:
    """Extract text from various content formats."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                texts.append(item.get("text", ""))
            elif isinstance(item, str):
                texts.append(item)
        return "\n".join(texts)
    return ""


def find_task_call_for_agent(parent_transcript_path: str, agent_id: str) -> dict:
    """
    Parse parent's transcript to find the Task tool call that spawned this agent.
    Returns dict with subagent_type and prompt.

    The transcript format is:
    {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Task", ...}]}}
    """
    result = {"subagent_type": "", "prompt": ""}

    try:
        path = Path(parent_transcript_path).expanduser()
        if not path.exists():
            return result

        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)

                    # Check for tool_use in message.content array (assistant messages)
                    message = entry.get("message", {})
                    content = message.get("content", [])
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and item.get("type") == "tool_use" and item.get("name") == "Task":
                                tool_input = item.get("input", {})
                                subagent_type = tool_input.get("subagent_type", "")
                                prompt = tool_input.get("prompt", "")

                                # Check if this is a backend-toolbox Task call with workflow context
                                if subagent_type.startswith("backend-toolbox:"):
                                    if "TASK_ID:" in prompt and "reportType:" in prompt:
                                        result["subagent_type"] = subagent_type
                                        result["prompt"] = prompt
                                        # Keep searching - later calls may be for our specific agent

                    # Also check direct tool_use entries (fallback for other formats)
                    if entry.get("type") == "tool_use" and entry.get("name") == "Task":
                        tool_input = entry.get("input", {})
                        subagent_type = tool_input.get("subagent_type", "")
                        prompt = tool_input.get("prompt", "")

                        if subagent_type.startswith("backend-toolbox:"):
                            if "TASK_ID:" in prompt and "reportType:" in prompt:
                                result["subagent_type"] = subagent_type
                                result["prompt"] = prompt

                except json.JSONDecodeError:
                    continue

    except Exception as e:
        print(f"Error parsing parent transcript: {e}", file=sys.stderr)

    return result


def parse_agent_transcript(agent_transcript_path: str) -> dict:
    """
    Parse the agent's own transcript to extract its output and prompt.
    Returns dict with prompt and transcript content.

    The transcript format is:
    {"type": "assistant|user|system", "message": {"content": [...]}}
    or
    {"type": "assistant|user|system", "content": "..."}
    """
    result = {"prompt": "", "transcript": ""}

    try:
        path = Path(agent_transcript_path).expanduser()
        if not path.exists():
            return result

        transcript_lines = []
        prompt_parts = []

        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    entry_type = entry.get("type", "")

                    # Try to get content from message.content or direct content
                    message = entry.get("message", {})
                    content = message.get("content") if message else entry.get("content", "")

                    # Extract text from content
                    text = ""
                    if isinstance(content, str):
                        text = content
                    elif isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict):
                                if item.get("type") == "text":
                                    text += item.get("text", "") + "\n"
                            elif isinstance(item, str):
                                text += item + "\n"
                    text = text.strip()

                    # Look for TASK_ID in system/user messages to find the original prompt
                    if entry_type in ("system", "user"):
                        if "TASK_ID:" in text and "reportType:" in text:
                            prompt_parts.append(text)

                    # Collect assistant messages for transcript
                    if entry_type == "assistant":
                        if text:
                            transcript_lines.append(text)

                    # Also check for text content in tool results
                    if entry_type == "tool_result":
                        if text:
                            transcript_lines.append(text)

                except json.JSONDecodeError:
                    continue

        # Use the first prompt part that contains workflow context
        if prompt_parts:
            result["prompt"] = prompt_parts[0]

        result["transcript"] = "\n".join(transcript_lines)

    except Exception as e:
        print(f"Error parsing agent transcript: {e}", file=sys.stderr)

    return result


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({}))
        return

    # Debug: Log all received fields to understand the actual input
    debug_path = Path("/tmp/subagent-stop-debug.log")
    try:
        with open(debug_path, "a") as f:
            f.write(f"--- SubagentStop hook received ---\n")
            f.write(json.dumps(data, indent=2, default=str))
            f.write("\n\n")
    except Exception:
        pass

    # SubagentStop provides transcript_path (parent) and agent_transcript_path (agent)
    parent_transcript_path = data.get("transcript_path", "")
    agent_transcript_path = data.get("agent_transcript_path", "")
    agent_id = data.get("agent_id", "")

    if not parent_transcript_path and not agent_transcript_path:
        try:
            with open(debug_path, "a") as f:
                f.write("Skipping: no transcript paths provided\n\n")
        except Exception:
            pass
        print(json.dumps({}))
        return

    # Parse the parent transcript to find the Task call that spawned this agent
    task_info = find_task_call_for_agent(parent_transcript_path, agent_id)
    subagent_type = task_info["subagent_type"]

    if not subagent_type.startswith("backend-toolbox:"):
        # Debug: log why we're exiting
        try:
            with open(debug_path, "a") as f:
                f.write(f"Skipping: subagent_type='{subagent_type}' (not backend-toolbox)\n\n")
        except Exception:
            pass
        print(json.dumps({}))
        return

    # Parse the agent's transcript to get its output
    agent_data = parse_agent_transcript(agent_transcript_path)

    # Get prompt from agent's own transcript (preferred - always correct)
    # Fall back to parent transcript only if agent transcript is empty
    # Note: Parent transcript may have NEWER Task calls from subsequent steps
    # if the orchestrator moved on while this agent was still finishing
    prompt = agent_data["prompt"] or task_info["prompt"]
    if not isinstance(prompt, str) or not prompt:
        # Debug: log why we're exiting
        try:
            with open(debug_path, "a") as f:
                f.write(f"Skipping: prompt not found in transcripts\n\n")
        except Exception:
            pass
        print(json.dumps({}))
        return

    # Parse workflow context
    ctx = parse_workflow_context(prompt)
    if not ctx["task_id"] or not ctx["report_type"]:
        # Debug: log why we're exiting
        try:
            with open(debug_path, "a") as f:
                f.write(f"Skipping: couldn't parse workflow context from prompt\n")
                f.write(f"  task_id={ctx['task_id']}, report_type={ctx['report_type']}\n")
                f.write(f"  prompt preview: {prompt[:200]}...\n\n")
        except Exception:
            pass
        print(json.dumps({}))
        return

    task_id = ctx["task_id"]
    report_type = ctx["report_type"]

    # Get transcript from agent's output
    transcript = agent_data["transcript"]

    # Check if report and signal already exist
    base = get_task_reports_base()
    report_file = base / task_id / "reports" / f"{report_type}.md"
    signal_file = base / task_id / "signals" / f"{report_type}.json"

    report_existed = report_file.exists()
    signal_existed = signal_file.exists()

    # Extract and save report (always, even if it exists - hook has final say)
    markdown_content = extract_markdown_sections(str(transcript))
    report_saved = save_report(task_id, report_type, markdown_content)

    # Parse and save signal (always, even if it exists - hook has final say)
    status, summary = parse_status_from_transcript(str(transcript))
    signal_saved = save_signal(task_id, report_type, status, summary)

    # Report results
    if report_saved and signal_saved:
        action = "Updated" if (report_existed or signal_existed) else "Auto-saved"
        # Debug: log success
        try:
            with open(debug_path, "a") as f:
                f.write(f"SUCCESS: {action} report and signal for {task_id}/{report_type} (status={status})\n\n")
        except Exception:
            pass
        print(json.dumps({
            "message": f"{action} report and signal for {report_type} (status={status})"
        }))
    else:
        errors = []
        if not report_saved:
            errors.append("report")
        if not signal_saved:
            errors.append("signal")
        # Debug: log failure
        try:
            with open(debug_path, "a") as f:
                f.write(f"FAILED: couldn't save {' and '.join(errors)} for {task_id}/{report_type}\n\n")
        except Exception:
            pass
        print(json.dumps({
            "error": f"Failed to auto-save {' and '.join(errors)} for {report_type}"
        }))


if __name__ == "__main__":
    main()
