#!/usr/bin/env python3
import json
import sys

IO_BLOCK = """
## Workflow I/O Contract (MANDATORY)

You MUST use these Bash scripts for all workflow persistence and retrieval.
Scripts are located at: ${CLAUDE_PLUGIN_ROOT}/scripts/workflow-io/

### Persistence Commands

**save-report.sh** - Save your full report content
```bash
${CLAUDE_PLUGIN_ROOT}/scripts/workflow-io/save-report.sh <taskId> <reportType> <content>
# Or pipe content:
echo "<content>" | ${CLAUDE_PLUGIN_ROOT}/scripts/workflow-io/save-report.sh <taskId> <reportType>
```
- reportType: requirements | codebase-analysis | plan | tests-design | tests-review | implementation | stabilization | acceptance | performance | security | refactoring | code-review | documentation

**save-signal.sh** - Save status signal (triggers step progression when waited)
```bash
${CLAUDE_PLUGIN_ROOT}/scripts/workflow-io/save-signal.sh <taskId> <signalType> <status> <summary>
```
- signalType: same as reportType
- status: "passed" | "failed"
- summary: one sentence describing outcome

### Retrieval Commands

**get-report.sh** - Retrieve a previously saved report
```bash
${CLAUDE_PLUGIN_ROOT}/scripts/workflow-io/get-report.sh <taskId> <reportType>
```
Returns: report content (markdown)

**get-metadata.sh** - Get task metadata
```bash
${CLAUDE_PLUGIN_ROOT}/scripts/workflow-io/get-metadata.sh <taskId>
```
Returns: JSON with taskId, executionSteps, currentStepIndex, startedAt, savedAt, completedAt

### Rules

1. For any "Input Reports" in your prompt, retrieve them via get-report.sh
2. Do NOT rely on TaskOutput, prior context, or local files as source of truth.
3. Always save both report AND signal when your step completes.
4. On failure, save signal with status "failed" and summary starting with "ERROR:"
""".strip()

data = json.load(sys.stdin)
tool_input = data.get("tool_input") or {}

subagent_type = tool_input.get("subagent_type", "")
if not subagent_type.startswith("backend-toolbox:"):
    print(json.dumps({}))
    sys.exit(0)

prompt = tool_input.get("prompt")
if isinstance(prompt, str) and IO_BLOCK not in prompt:
    tool_input["prompt"] = f"{IO_BLOCK}\n\n{prompt}"

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "allow",
        "permissionDecisionReason": "Auto-inject workflow I/O contract into subagent prompts",
        "updatedInput": tool_input
    }
}))
