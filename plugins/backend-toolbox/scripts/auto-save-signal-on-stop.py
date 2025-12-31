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

    # Extract Output reportType
    output_match = re.search(r'##\s*Output\s*\n\s*reportType:\s*(\S+)', prompt)
    if output_match:
        result["report_type"] = output_match.group(1)

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


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({}))
        return

    subagent_type = data.get("subagent_type", "")
    if not subagent_type.startswith("backend-toolbox:"):
        print(json.dumps({}))
        return

    prompt = data.get("prompt", "")
    if not isinstance(prompt, str):
        print(json.dumps({}))
        return

    # Parse workflow context
    ctx = parse_workflow_context(prompt)
    if not ctx["task_id"] or not ctx["report_type"]:
        print(json.dumps({}))
        return

    task_id = ctx["task_id"]
    report_type = ctx["report_type"]

    # Get transcript
    transcript = data.get("transcript", "")
    if not transcript:
        transcript = data.get("response", "")

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
        print(json.dumps({
            "message": f"{action} report and signal for {report_type} (status={status})"
        }))
    else:
        errors = []
        if not report_saved:
            errors.append("report")
        if not signal_saved:
            errors.append("signal")
        print(json.dumps({
            "error": f"Failed to auto-save {' and '.join(errors)} for {report_type}"
        }))


if __name__ == "__main__":
    main()
