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
    # Check for explicit override
    override = os.environ.get("TASK_REPORTS_BASE")
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


def analyze_transcript_for_status(transcript: str) -> tuple[str, str]:
    """
    Analyze agent transcript to determine pass/fail status.
    Returns (status, summary).
    """
    transcript_lower = transcript.lower()

    # Check for explicit failure indicators
    failure_indicators = [
        "error:", "failed:", "exception:", "traceback:",
        "could not", "unable to", "cannot find", "not found",
        "assertion error", "test failed", "tests failed",
        "status: failed", "status=failed"
    ]

    for indicator in failure_indicators:
        if indicator in transcript_lower:
            # Try to extract a meaningful summary
            lines = transcript.split('\n')
            for line in lines:
                if indicator.replace(":", "") in line.lower():
                    return "failed", f"ERROR: {line[:100].strip()}"
            return "failed", "ERROR: Agent encountered issues (auto-detected)"

    # Check for success indicators
    success_indicators = [
        "all tests pass", "tests passing", "completed successfully",
        "implementation complete", "review complete", "analysis complete",
        "status: passed", "status=passed", "no issues found",
        "requirements met", "approved"
    ]

    for indicator in success_indicators:
        if indicator in transcript_lower:
            return "passed", "Completed successfully (auto-detected from transcript)"

    # Default to passed if no clear failure
    return "passed", "Agent completed (signal auto-saved by hook)"


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
        # No valid input, skip
        print(json.dumps({}))
        return

    # Get the subagent type
    subagent_type = data.get("subagent_type", "")
    if not subagent_type.startswith("backend-toolbox:"):
        # Not our agent, skip
        print(json.dumps({}))
        return

    # Get the original prompt to extract workflow context
    prompt = data.get("prompt", "")
    if not isinstance(prompt, str):
        print(json.dumps({}))
        return

    # Parse workflow context
    ctx = parse_workflow_context(prompt)
    if not ctx["task_id"] or not ctx["report_type"]:
        # Not a workflow agent, skip
        print(json.dumps({}))
        return

    task_id = ctx["task_id"]
    report_type = ctx["report_type"]

    # Check if signal already exists
    base = get_task_reports_base()
    signal_file = base / task_id / "signals" / f"{report_type}.json"

    if signal_file.exists():
        # Agent already saved signal, nothing to do
        print(json.dumps({}))
        return

    # Signal missing - auto-save it
    transcript = data.get("transcript", "")
    if not transcript:
        transcript = data.get("response", "")

    status, summary = analyze_transcript_for_status(str(transcript))

    if save_signal(task_id, report_type, status, summary):
        print(json.dumps({
            "message": f"Auto-saved missing signal for {report_type} (status={status})"
        }))
    else:
        print(json.dumps({
            "error": f"Failed to auto-save signal for {report_type}"
        }))


if __name__ == "__main__":
    main()
