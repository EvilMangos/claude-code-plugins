#!/usr/bin/env python3
import json
import sys

MCP_BLOCK = """
## MCP I/O Contract (MANDATORY)

Persistence (ONLY via MCP):
- You MUST persist your outputs via MCP tools:
  - save-report (full report content)
  - save-signal (status + 1-sentence summary)
- Writing files (e.g. .task-reports/*) does NOT count as saving.

Retrieval (ONLY via MCP):
- For any "Input Reports" listed in your step prompt, you MUST retrieve them via MCP get-report
  (taskId + reportType).
- Do NOT rely on TaskOutput, prior context, or local files as the source of truth for inputs.

Failure handling:
- If you cannot retrieve a required report via get-report, or cannot save via MCP, you MUST:
  - save-signal with status: "failed"
  - summary starting with "ERROR:" describing what failed
""".strip()

data = json.load(sys.stdin)

tool_name = data.get("tool_name")
tool_input = data.get("tool_input") or {}

if tool_name != "Task":
    print(json.dumps({}))
    sys.exit(0)

prompt = tool_input.get("prompt")
if isinstance(prompt, str) and MCP_BLOCK not in prompt:
    tool_input["prompt"] = f"{MCP_BLOCK}\n\n{prompt}"

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "allow",
        "permissionDecisionReason": "Auto-inject MCP save/retrieve contract into subagent prompts",
        "updatedInput": tool_input
    }
}))
