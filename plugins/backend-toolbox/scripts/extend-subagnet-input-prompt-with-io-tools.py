#!/usr/bin/env python3
import json
import re
import sys

IO_BLOCK_TEMPLATE = """
## Workflow I/O Contract

You are part of a multi-agent workflow. TASK_ID: `{task_id}`

### Available Script

You have access to `get-report.sh` (via your Bash tool allowlist):
```
get-report.sh <taskId> <reportType>
```
Returns markdown content of a previous agent's report. If report doesn't exist yet, returns a "not available" message - skip and continue.

### Input: Fetch These Reports

{fetch_commands}

**⚠️ Reports contain summaries from previous agents, NOT current file content.**
Always verify by reading actual files with Read/Glob/Grep before making judgments.

### Output: `{report_type}`

Your response is auto-captured as the workflow report. Required format:
1. Use `## Heading` sections for structure
2. End with `STATUS: PASSED` or `STATUS: FAILED`

Example:
```markdown
## Summary
[What you did]

## Findings
[Details]

STATUS: PASSED
```
""".strip()


def parse_workflow_context(prompt: str) -> dict:
    """Extract TASK_ID, Input Reports, and Output reportType from prompt."""
    result = {"task_id": None, "report_type": None, "input_reports": []}

    # Extract TASK_ID (first line usually)
    task_match = re.search(r'TASK_ID:\s*(\S+)', prompt)
    if task_match:
        result["task_id"] = task_match.group(1)

    # Extract Output reportType
    output_match = re.search(r'##\s*Output\s*\n\s*reportType:\s*(\S+)', prompt)
    if output_match:
        result["report_type"] = output_match.group(1)

    # Extract Input Reports (list items after "## Input Reports")
    input_section = re.search(r'##\s*Input Reports\s*\n((?:\s*(?:Required:|Optional[^:]*:)?\s*\n?(?:\s*-\s*\S+\s*\n?)+)+)', prompt)
    if input_section:
        reports = re.findall(r'-\s*(\S+)', input_section.group(1))
        result["input_reports"] = [r for r in reports if r not in ('Required:', 'Optional')]

    return result

def build_io_block(ctx: dict) -> str:
    """Build the IO block with extracted context."""
    if not ctx["task_id"] or not ctx["report_type"]:
        return None

    fetch_commands = ""
    if ctx["input_reports"]:
        reports_list = "\n".join(f"get-report.sh {ctx['task_id']} {r}" for r in ctx["input_reports"])
        fetch_commands = f"```bash\n{reports_list}\n```"
    else:
        fetch_commands = "(none - skip this step)"

    return IO_BLOCK_TEMPLATE.format(
        task_id=ctx["task_id"],
        report_type=ctx["report_type"],
        fetch_commands=fetch_commands
    )


data = json.load(sys.stdin)
tool_input = data.get("tool_input") or {}

subagent_type = tool_input.get("subagent_type", "")
if not subagent_type.startswith("backend-toolbox:"):
    print(json.dumps({}))
    sys.exit(0)

prompt = tool_input.get("prompt", "")
if not isinstance(prompt, str):
    print(json.dumps({}))
    sys.exit(0)

# Skip if already injected
if "## Workflow I/O Contract" in prompt:
    print(json.dumps({}))
    sys.exit(0)

# Parse and build IO block
ctx = parse_workflow_context(prompt)
io_block = build_io_block(ctx)

# Only modify if we have workflow context (TASK_ID + reportType)
if not io_block:
    # No workflow context - skip injection, let agent run normally
    print(json.dumps({}))
    sys.exit(0)

tool_input["prompt"] = f"{io_block}\n\n---\n\n{prompt}"

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "allow",
        "permissionDecisionReason": "Auto-inject workflow I/O contract into subagent prompts",
        "updatedInput": tool_input
    }
}))
