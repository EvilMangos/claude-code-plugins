---
description: Fix a bug using a structured workflow with reproduction, root cause analysis, TDD, implementation, and code review.
argument-hint: <bug-description>
allowed-tools: Read, Edit, Write, Grep, Glob, Task, Skill, MCP
---

# Bug Fix Workflow (Background Agent Orchestration)

You are orchestrating a multistep **bug-fixing** workflow for this repository.

The bug report is:

> $ARGUMENTS

## Architecture: Workflow

This workflow drives all decisions:

1. **Orchestrator initializes task** with metadata
2. **The workflow determines the next step** based on current state
3. **Orchestrator executes the step** returned by the workflow
4. **Agent saves report and signal**
5. **Orchestrator queries for next step** - repeat until complete

**The orchestrator NEVER decides which step to run next. The workflow makes all routing decisions.**

## Workflow Scripts

All orchestrator operations use scripts in `${CLAUDE_PLUGIN_ROOT}/scripts/workflow-io/`:

| Operation | Script | Usage |
|-----------|--------|-------|
| Create metadata | `create-metadata.sh <taskId> '<stepsJson>'` | Initialize task with execution steps |
| Get next step | `get-next-step.sh <taskId>` | Returns current step to execute |
| Wait for signal | `wait-signal.sh <taskId> <signalType(s)> [timeout]` | Waits for signal(s), advances workflow |
| Get report | `get-report.sh <taskId> <reportType>` | Retrieves full report content |

Notes:
- `stepsJson` is a JSON array, arrays within represent parallel steps: `'["plan",["perf","security"],"impl"]'`
- For parallel signals, use comma-separated types: `wait-signal.sh $TASK_ID "performance,security"`
- Scripts output JSON to stdout; parse with jq

## Task ID Generation

Before starting, generate a unique task ID for this workflow:

```
TASK_ID = fix-bug-{slug}-{timestamp}
```

Where:
- `slug`: URL-safe version of bug description (lowercase, hyphens, max 30 chars)
  - Example: "Login fails with special chars" → `login-fails-special-chars`
  - Example: "Memory leak in cache" → `memory-leak-in-cache`
- `timestamp`: Unix timestamp in seconds (e.g., `1702834567`)

Example: `fix-bug-login-fails-special-chars-1702834567`

## Orchestrator Loop

After initialization, the orchestrator runs this loop:

```
LOOP:
  1. Get next step (returns: stepNumber, totalSteps, step, complete)

  2. IF complete == true:
     - Output final signal summary to user
     - EXIT LOOP

  3. Launch the agent for the returned step
     - For "requirements" step: run_in_background: false (needs user interaction)
     - For all other steps: run_in_background: true

  4. Wait for signal

  5. GOTO 1
END LOOP
```

**Critical Rules:**

1. **The orchestrator does NOT interpret signal status to decide next step. It always queries the workflow.**

2. **Always execute the step returned, even if that step was already executed before.**
   - The workflow may return the same step multiple times (e.g., `tests-design` after a failed `tests-review`)
   - This is intentional: the workflow handles retry logic and gate failures internally
   - Do NOT skip a step because "it was already done"
   - Simply execute whatever step is returned, every time

3. **NEVER use TaskOutput to retrieve background agent results.**
   - Background agents communicate ONLY via signals and reports
   - If you need agent results: use get-report script, NOT TaskOutput

## Agent Output Instructions

**Always include these instructions in every agent prompt:**
```
## Workflow Context
TASK_ID: {TASK_ID}

## Output
1. Save your FULL report:
   - taskId: {TASK_ID}
   - reportType: {report-type}
   - content: <your full report content>

2. Save your signal:
   - taskId: {TASK_ID}
   - signalType: {report-type}
   - content:
     - status: "passed" or "failed"
     - summary: {one sentence describing outcome}

   Status mapping:
   - "passed" = completed successfully, gate passed, no issues found
   - "failed" = needs iteration, has issues to resolve, or error occurred
     (include details in summary: "PARTIAL: ...", "ISSUES: N", "ERROR: ...")
```

---

## Step Definitions

### initialize

Create task metadata:
- taskId: {TASK_ID}
- executionSteps: `["requirements", "codebase-analysis", "plan", "tests-design", "tests-review", "implementation", "stabilization", "acceptance", "code-review", "refactoring", "finalize"]`

### Step 1: requirements (business-analyst)

```
subagent_type: business-analyst
run_in_background: false
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Analyze the bug report and clarify requirements:
  - Restate the bug in your own words
  - Identify the expected behavior vs actual behavior
  - Identify affected domains/packages/components
  - List ALL ambiguous points or missing details
  - If ambiguities exist: ask ALL questions using AskUserQuestion tool
  - Document assumptions explicitly

  ## Bug Report
  $ARGUMENTS

  ## Output
  1. Save FULL report:
     - taskId: {TASK_ID}
     - reportType: "requirements"
     - content: Include Bug Understanding, Expected vs Actual, Affected Components, Clarifications, Assumptions
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "requirements"
     - content: { status: "passed", summary: "Bug requirements clarified" }
```

### Step 2: codebase-analysis (codebase-analyzer)

```
subagent_type: codebase-analyzer
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Analyze the codebase to:
  1. Attempt to reproduce the bug (run existing tests, trace code paths)
  2. Perform root cause analysis:
     - Trace the code path from symptom to source
     - Check recent changes if relevant (git log, git blame)
     - Identify specific file(s), function(s), and line(s) causing the issue

  Document:
  - Reproduction steps and evidence
  - Root cause explanation
  - Why the bug occurs (missing check, wrong logic, race condition, etc.)
  - Confidence level (certain, likely, hypothesis)

  If bug cannot be reproduced, signal "failed" with details requesting more info.

  ## Input Reports
  Retrieve (taskId={TASK_ID}):
  - reportType: "requirements"

  ## Output
  1. Save FULL report:
     - taskId: {TASK_ID}
     - reportType: "codebase-analysis"
     - content: <reproduction steps, root cause analysis, affected files>
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "codebase-analysis"
     - content: { status: "passed" or "failed", summary: "..." }
```

### Step 3: plan (plan-creator)

```
subagent_type: plan-creator
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Create a fix plan based on the root cause analysis:
  - Step-by-step fix plan
  - Risk assessment (could this fix break other things?)
  - Files to modify and how
  - Test strategy (what tests to add/modify)

  ## Input Reports
  Retrieve (taskId={TASK_ID}):
  - reportType: "requirements"
  - reportType: "codebase-analysis"

  ## Output
  1. Save FULL report:
     - taskId: {TASK_ID}
     - reportType: "plan"
     - content: <your fix plan>
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "plan"
     - content: { status: "passed", summary: "Fix plan created" }
```

### Step 4: tests-design (automation-qa)

```
subagent_type: automation-qa
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Design and write tests for the bug fix (RED stage).
  - Evaluate whether a regression test is warranted (use test-best-practices skill)
  - If warranted: write a test that reproduces the bug (should FAIL with current code)
  - If not warranted: document why and proceed without a test

  If a test was created, run it to confirm it FAILS (RED).
  If the test passes unexpectedly, signal "failed" - the bug may not be where we think.

  ## Input Reports
  Retrieve (taskId={TASK_ID}):
  Required:
  - reportType: "requirements"
  - reportType: "codebase-analysis"
  - reportType: "plan"
  Optional (contains feedback requiring test updates):
  - reportType: "tests-review"
  - reportType: "stabilization"
  - reportType: "acceptance"
  - reportType: "code-review"

  ## Output
  1. Save FULL report:
     - taskId: {TASK_ID}
     - reportType: "tests-design"
     - content: <test design report, whether test was created, RED verification>
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "tests-design"
     - content: { status: "passed" or "failed", summary: "..." }
```

### Step 5: tests-review (tests-reviewer)

```
subagent_type: tests-reviewer
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Review the bug-catching test (if created):
  - Does the test actually catch the reported bug?
  - Is the test assertion specific enough?
  - Will the test remain valuable after the fix (regression prevention)?

  If no test was created (automation-qa determined not warranted), verify the reasoning.

  Return verdict in signal:
  - status: "passed" = test quality is acceptable (or no-test decision was valid)
  - status: "failed" = test needs improvement (include "PARTIAL: ..." in summary)

  ## Input Reports
  Retrieve (taskId={TASK_ID}):
  - reportType: "requirements"
  - reportType: "codebase-analysis"
  - reportType: "plan"
  - reportType: "tests-design"

  ## Output
  1. Save FULL report:
     - taskId: {TASK_ID}
     - reportType: "tests-review"
     - content: <your test review report with verdict>
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "tests-review"
     - content: { status: "passed" or "failed", summary: "..." }
```

### Step 6: implementation (backend-developer)

```
subagent_type: backend-developer
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Implement the bug fix (GREEN stage):
  - Follow the fix plan
  - Work in small, incremental steps
  - After each step, run tests with the smallest relevant scope
  - The bug-catching test (if created) should now PASS (GREEN)

  ## Input Reports
  Retrieve (taskId={TASK_ID}):
  Required:
  - reportType: "requirements"
  - reportType: "codebase-analysis"
  - reportType: "plan"
  - reportType: "tests-design"
  Optional (contains feedback requiring fixes):
  - reportType: "tests-review"
  - reportType: "stabilization"
  - reportType: "acceptance"
  - reportType: "code-review"

  ## Output
  1. Save FULL report:
     - taskId: {TASK_ID}
     - reportType: "implementation"
     - content: <implementation report, what changed, test results>
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "implementation"
     - content: { status: "passed" or "failed", summary: "..." }
```

### Step 7: stabilization (automation-qa)

```
subagent_type: automation-qa
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Run broader test scope and assess stability:
  - Determine if additional regression tests are needed
  - Run package-level or broader tests
  - Identify any regressions introduced

  Return verdict in signal:
  - status: "passed" = stable, no regressions
  - status: "failed" = issues found (include "PARTIAL: ..." in summary)

  ## Input Reports
  Retrieve (taskId={TASK_ID}):
  - reportType: "requirements"
  - reportType: "plan"
  - reportType: "implementation"

  ## Output
  1. Save FULL report:
     - taskId: {TASK_ID}
     - reportType: "stabilization"
     - content: <stabilization report with broader test results>
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "stabilization"
     - content: { status: "passed" or "failed", summary: "..." }
```

### Step 8: acceptance (acceptance-reviewer)

```
subagent_type: acceptance-reviewer
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Verify the bug is fixed:
  - Check original bug is resolved
  - Verify no new issues were introduced
  - Confirm fix matches expected behavior from requirements

  Return verdict in signal:
  - status: "passed" = bug fixed, acceptance criteria met
  - status: "failed" = gaps found (include "PARTIAL: ..." in summary)

  ## Input Reports
  Retrieve (taskId={TASK_ID}):
  - reportType: "requirements"
  - reportType: "codebase-analysis"
  - reportType: "plan"
  - reportType: "implementation"
  - reportType: "stabilization"

  ## Output
  1. Save FULL report:
     - taskId: {TASK_ID}
     - reportType: "acceptance"
     - content: <acceptance review report with verdict>
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "acceptance"
     - content: { status: "passed" or "failed", summary: "..." }
```

### Step 9: code-review (code-reviewer)

```
subagent_type: code-reviewer
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Review the bug fix for quality:
  - Fix quality (is this the right solution?)
  - Adherence to project conventions
  - No unnecessary changes beyond the fix
  - Test quality (if tests were added)

  Apply your loaded skills (`code-review-checklist`, `design-assessment`).
  For each issue, specify route:
  - "ROUTE: functional" → needs tests + implementation fix
  - "ROUTE: structural" → needs refactoring

  Return verdict in signal:
  - status: "passed" = no issues found
  - status: "failed" = issues found (include "ISSUES: N functional, M structural" in summary)

  ## Input Reports
  Retrieve (taskId={TASK_ID}):
  - reportType: "codebase-analysis"
  - reportType: "plan"
  - reportType: "implementation"
  - reportType: "stabilization"

  ## Output
  1. Save FULL report:
     - taskId: {TASK_ID}
     - reportType: "code-review"
     - content: <code review report with verdict>
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "code-review"
     - content: { status: "passed" or "failed", summary: "..." }
```

### Step 10: refactoring (refactorer)

```
subagent_type: refactorer
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Perform behavior-preserving cleanup if code-review identified structural issues.
  - Improve structure, naming, clarity
  - Keep external behavior identical
  - Run tests after each refactor step

  Do not expand scope beyond what's needed for the bug fix.

  Apply your loaded skills (`refactoring-patterns`, `design-assessment`).

  ## Input Reports
  Retrieve (taskId={TASK_ID}):
  - reportType: "codebase-analysis"
  - reportType: "implementation"
  - reportType: "code-review"

  ## Output
  1. Save FULL report:
     - taskId: {TASK_ID}
     - reportType: "refactoring"
     - content: <refactoring report>
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "refactoring"
     - content: { status: "passed", summary: "Refactoring complete, tests passing" }
```

### Step 11: finalize (workflow-finalizer)

```
subagent_type: workflow-finalizer
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Generate an executive summary of the completed bug fix workflow.

  Read all available reports for this task and synthesize:
  - Overall outcome (success/partial/failed)
  - Root cause identified
  - Fix applied
  - Open items/follow-ups (if any)
  - Files changed

  Keep the summary concise and focused on outcomes.

  ## Output
  1. Save FULL report:
     - taskId: {TASK_ID}
     - reportType: "finalize"
     - content: <your executive summary>
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "finalize"
     - content: { status: "passed", summary: "Bug fix complete: <one-sentence outcome>" }
```

After the finalize signal is received, the orchestrator outputs the signal summary to the user and exits.

---

## Non-negotiable constraints

- Reproduce or verify the bug before attempting to fix it.
- Always invoke automation-qa to evaluate whether a regression test is needed.
- After every implementation or refactor step, run tests with the smallest relevant scope.
- Do not introduce changes beyond what's needed to fix the reported bug.
- Prefer narrow test scopes unless broader runs are required by the workflow.
