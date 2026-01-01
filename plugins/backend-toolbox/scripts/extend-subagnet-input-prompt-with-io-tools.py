#!/usr/bin/env python3
import json
import re
import sys

IO_BLOCK_TEMPLATE = """
## Workflow I/O Contract (MANDATORY)

You are part of a multi-agent workflow. Follow these requirements exactly.

### Your Workflow Context

- **TASK_ID**: `{task_id}`
- **Output reportType**: `{report_type}`
- **Input Reports available**: {input_reports}

### Step 1: Fetch Input Reports (if needed)

{fetch_commands}

Read the returned content - this is context from previous workflow steps.
**NOTE**: If a report doesn't exist yet (file not found error), that's expected for early workflow steps - skip that report and continue.

### Step 2: Complete Your Work

Complete your assigned task using the fetched reports as context.

### Step 3: Structure Your Output (MANDATORY)

Your response will be automatically captured and saved as the workflow report.

**Required format:**
1. Structure your report using markdown sections with ## headings
2. Include all analysis, findings, decisions, and recommendations
3. End your response with a clear status declaration:
   - `STATUS: PASSED` if you successfully completed your task
   - `STATUS: FAILED` if you encountered blocking issues

**Example structure:**
```markdown
## Summary
[Brief overview of what you did]

## Analysis
[Your detailed analysis]

## Recommendations
[Your recommendations or next steps]

STATUS: PASSED
```

### Critical Rules

1. **Structure with markdown headings** - Use ## for all major sections so they can be properly captured
2. **Always end with STATUS** - The orchestrator needs to know if you succeeded or failed
3. **Fetch before working** - Read all input reports before starting your analysis (skip missing ones)
4. **STATUS: FAILED on errors** - If you encounter blocking issues, declare failure explicitly
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

    input_reports_str = ", ".join(f"`{r}`" for r in ctx["input_reports"]) if ctx["input_reports"] else "(none)"

    fetch_commands = ""
    if ctx["input_reports"]:
        fetch_commands = "Run these commands:\n" + "\n".join(
            f"```bash\n${{CLAUDE_PLUGIN_ROOT}}/scripts/workflow-io/get-report.sh {ctx['task_id']} {r}\n```"
            for r in ctx["input_reports"]
        )
    else:
        fetch_commands = "(No input reports to fetch - skip this step)"

    return IO_BLOCK_TEMPLATE.format(
        task_id=ctx["task_id"],
        report_type=ctx["report_type"],
        input_reports=input_reports_str,
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
