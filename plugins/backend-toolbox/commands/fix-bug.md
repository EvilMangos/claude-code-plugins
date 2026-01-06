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
| Wait for signal | `wait-signal.sh <taskId> <signalType(s)>` | Waits for signal(s), advances workflow |
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
  TASK_ID: {TASK_ID}

  ## Task
  Analyze the bug report and clarify requirements:
  - Restate the bug in your own words
  - Identify the expected behavior vs actual behavior
  - Identify affected domains/packages/components
  - List ALL ambiguous points or missing details
  - If ambiguities exist: output BLOCKED status with questions (do NOT make assumptions)
  - If no ambiguities (or clarifications provided below): document clear requirements

  ## Bug Report
  $ARGUMENTS

  {CLARIFICATIONS_BLOCK}

  ## Output
  reportType: requirements
```

**Handling BLOCKED status:**

After invoking business-analyst, check the signal status:
1. If signal status is `blocked`:
   - Read the requirements report to get the questions
   - Use `AskUserQuestion` tool to ask the user ALL questions at once
   - Re-invoke business-analyst with the same prompt, but add a `## Clarifications Provided` section containing the user's answers
   - Replace `{CLARIFICATIONS_BLOCK}` with the clarifications section
   - Repeat until signal status is `passed`
2. If signal status is `passed`:
   - Proceed to next step

### Step 2: codebase-analysis (codebase-analyzer)

```
subagent_type: codebase-analyzer
run_in_background: true
prompt: |
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
  - requirements

  ## Output
  reportType: codebase-analysis
```

### Step 3: plan (plan-creator)

```
subagent_type: plan-creator
run_in_background: true
prompt: |
  TASK_ID: {TASK_ID}

  ## Task
  Create a fix plan based on the root cause analysis:
  - Step-by-step fix plan
  - Risk assessment (could this fix break other things?)
  - Files to modify and how
  - Test strategy (what tests to add/modify)

  ## Input Reports
  - requirements
  - codebase-analysis

  ## Output
  reportType: plan
```

### Step 4: tests-design (automation-qa)

```
subagent_type: automation-qa
run_in_background: true
prompt: |
  TASK_ID: {TASK_ID}

  ## Task
  Design and write tests for the bug fix (RED stage).
  - Evaluate whether a regression test is warranted (use test-best-practices skill)
  - If warranted: write a test that reproduces the bug (should FAIL with current code)
  - If not warranted: document why and proceed without a test

  If a test was created, run it to confirm it FAILS (RED).
  If the test passes unexpectedly, signal "failed" - the bug may not be where we think.

  ## Input Reports
  Required:
  - requirements
  - codebase-analysis
  - plan
  Optional (contains feedback requiring test updates):
  - tests-review
  - stabilization
  - acceptance
  - code-review

  ## Output
  reportType: tests-design
```

### Step 5: tests-review (tests-reviewer)

```
subagent_type: tests-reviewer
run_in_background: true
prompt: |
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
  - requirements
  - codebase-analysis
  - plan
  - tests-design

  ## Output
  reportType: tests-review
```

### Step 6: implementation (backend-developer)

```
subagent_type: backend-developer
run_in_background: true
prompt: |
  TASK_ID: {TASK_ID}

  ## Task
  Implement the bug fix (GREEN stage):
  - Follow the fix plan
  - Work in small, incremental steps
  - After each step, run tests with the smallest relevant scope
  - The bug-catching test (if created) should now PASS (GREEN)

  ## Input Reports
  Required:
  - requirements
  - codebase-analysis
  - plan
  - tests-design
  Optional (contains feedback requiring fixes):
  - tests-review
  - stabilization
  - acceptance
  - code-review

  ## Output
  reportType: implementation
```

### Step 7: stabilization (automation-qa)

```
subagent_type: automation-qa
run_in_background: true
prompt: |
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
  - requirements
  - plan
  - implementation

  ## Output
  reportType: stabilization
```

### Step 8: acceptance (acceptance-reviewer)

```
subagent_type: acceptance-reviewer
run_in_background: true
prompt: |
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
  - requirements
  - codebase-analysis
  - plan
  - implementation
  - stabilization

  ## Output
  reportType: acceptance
```

### Step 9: code-review (code-reviewer)

```
subagent_type: code-reviewer
run_in_background: true
prompt: |
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
  - codebase-analysis
  - plan
  - implementation
  - stabilization

  ## Output
  reportType: code-review
```

### Step 10: refactoring (refactorer)

```
subagent_type: refactorer
run_in_background: true
prompt: |
  TASK_ID: {TASK_ID}

  ## Task
  Perform behavior-preserving cleanup if code-review identified structural issues.
  - Improve structure, naming, clarity
  - Keep external behavior identical
  - Run tests after each refactor step

  Do not expand scope beyond what's needed for the bug fix.

  Apply your loaded skills (`refactoring-patterns`, `design-assessment`).

  ## Input Reports
  - codebase-analysis
  - implementation
  - code-review

  ## Output
  reportType: refactoring
```

### Step 11: finalize (workflow-finalizer)

```
subagent_type: workflow-finalizer
run_in_background: true
prompt: |
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
  reportType: finalize
```

After the finalize signal is received, the orchestrator outputs the signal summary to the user and exits.

---

## Non-negotiable constraints

- Reproduce or verify the bug before attempting to fix it.
- Always invoke automation-qa to evaluate whether a regression test is needed.
- After every implementation or refactor step, run tests with the smallest relevant scope.
- Do not introduce changes beyond what's needed to fix the reported bug.
- Prefer narrow test scopes unless broader runs are required by the workflow.
