---
description: Refactor tests within an optional path (file or folder). If no path is provided, scope is the entire test suite. Never modify non-test production code.
argument-hint: [ path ]
allowed-tools: Read, Edit, Grep, Glob, Bash(git:*), Bash(ls:*), Bash(find:*), Task, Skill, MCP
---

# Tests Refactor Workflow (Background Agent Orchestration)

You are orchestrating a **tests-refactor-only** workflow for this repository.

The user request is:

> $ARGUMENTS

The argument is an optional **path** to a test file or test folder. If no argument is provided, the scope is the **entire test suite**.

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
TASK_ID = refactor-tests-{slug}-{timestamp}
```

Where:
- `slug`: URL-safe version of path or "suite" (lowercase, hyphens, max 30 chars)
  - Example: "tests/unit/utils.test.ts" → `tests-unit-utils`
  - Example: (no path) → `suite`
- `timestamp`: Unix timestamp in seconds (e.g., `1702834567`)

Example: `refactor-tests-tests-unit-utils-1702834567`

## Hard constraints (non-negotiable)

1) **Tests-only changes**
   You may edit ONLY:
   - Test files / test folders (definitions below)
   - Test-only support files (definitions below)
   - Documentation files (for documentation step)

   You must NOT edit, create, delete, rename, or move **production code**.

2) **Behavior-preserving**
   - Do not intentionally change the meaning/coverage of the tests.
   - Refactor for readability, determinism, structure, and robustness.

3) **Tests after each step**
   - After **every refactor step** that changes files, run tests with the smallest relevant scope.

### Test File Patterns

See `skills/test-best-practices/references/test-file-patterns.md` for complete identification patterns.

Key patterns:
- **Test files**: `/test/`, `/tests/`, `/__tests__/`, files containing `.spec.` or `.test.`
- **Support files**: `/__mocks__/`, `/fixtures/`, `/testdata/`, `/test_utils/`
- **Documentation**: `README*`, `CHANGELOG*`, `docs/**` (for documentation step only)

If a required improvement would need production code changes, STOP and tell the user to use `/refactor` instead.

## Preflight (main agent)

Before initializing the workflow, the main agent must:

1) Determine scope:
   - If `$ARGUMENTS` is empty: scope = "entire test suite".
   - Else: scope = `$ARGUMENTS`.

2) Validate scope path (if provided):
   - Use Glob to confirm the path exists.
   - If it does not exist, STOP and report the path is invalid.
   - If it exists but does NOT look like a test file/folder by the definitions above, STOP and tell the user to use `/refactor`.

3) Establish baseline:
   - Run tests with the smallest reasonable scope.
   - If baseline fails, STOP: refactoring is blocked until tests are green.

## Orchestrator Loop

After initialization, the orchestrator runs this loop:

```
LOOP:
  1. Get next step (returns: stepNumber, totalSteps, step, complete)

  2. IF complete == true:
     - Output final signal summary to user
     - EXIT LOOP

  3. Launch the agent for the returned step (run_in_background: true)

  4. Wait for signal

  5. GOTO 1
END LOOP
```

**Critical Rules:**

1. **The orchestrator does NOT interpret signal status to decide next step. It always queries the workflow.**

2. **Always execute the step returned, even if that step was already executed before.**
   - The workflow may return the same step multiple times
   - Simply execute whatever step is returned, every time

3. **NEVER use TaskOutput to retrieve background agent results.**
   - Background agents communicate ONLY via signals and reports
   - If you need agent results: use get-report script, NOT TaskOutput

---

## Step Definitions

### initialize

Create task metadata:
- taskId: {TASK_ID}
- executionSteps: `["requirements", "codebase-analysis", "plan", "refactoring", "tests-review", "code-review", "acceptance", "documentation", "finalize"]`

### Step 1: requirements (main agent captures scope)

The main agent (not a subagent) captures:
- Scope (path or entire test suite)
- Success criteria: tests remain green, no production code changed, improved readability/structure/determinism
- Refactor goals: reduce duplication, simplify setup/teardown, clarify naming, remove flakiness, improve fixtures

Save report and signal with reportType/signalType: "requirements"

### Step 2: codebase-analysis (codebase-analyzer)

```
subagent_type: codebase-analyzer
run_in_background: true
prompt: |
  TASK_ID: {TASK_ID}
  SCOPE: {scope}

  ## Task
  Analyze the codebase to understand existing testing patterns and conventions.
  This analysis will guide refactoring to ensure consistency.

  Focus on:
  - Test organization and structure
  - Mocking and stubbing patterns
  - Fixture and factory patterns
  - Setup/teardown conventions
  - Naming conventions for tests

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
  SCOPE: {scope}

  ## Task
  Create a small-step refactor plan (each step independently testable).
  For each step include:
  - files to change (must be tests/support/docs only)
  - expected outcome
  - smallest test scope to run after the step

  If scope is the entire test suite: prioritize top 3-10 highest-value refactors.
  Add a "file-safety" section explaining how the plan avoids production code edits.

  ## Input Reports
  - requirements
  - codebase-analysis

  ## Output
  reportType: plan
```

### Step 4: refactoring (automation-qa)

```
subagent_type: automation-qa
run_in_background: true
prompt: |
  TASK_ID: {TASK_ID}
  SCOPE: {scope}

  ## Task
  Execute the refactor plan step-by-step.
  For each plan step:
  1) Apply minimal behavior-preserving edits (tests/support/docs only)
  2) Describe what changed (files + why)
  3) Run tests with the smallest relevant scope
  4) Check changed files with `git diff --name-only`
     - If any changed file is NOT a test/support/doc file: revert and STOP

  If tests fail: fix the refactor (or revert) with minimal changes, re-run tests.

  ## Input Reports
  Required:
  - codebase-analysis
  - plan
  Optional (contains feedback requiring fixes):
  - tests-review
  - code-review
  - acceptance

  ## Output
  reportType: refactoring
```

### Step 5: tests-review (tests-reviewer)

```
subagent_type: tests-reviewer
run_in_background: true
prompt: |
  TASK_ID: {TASK_ID}

  ## Task
  Review the refactored tests for quality.
  Apply your loaded skill (`test-best-practices`).

  Verify:
  - Test meaning/coverage preserved
  - No production code modified
  - Improved readability, determinism, structure

  Signal status:
  - "passed" = tests meet quality standards
  - "failed" = issues found (include "PARTIAL: ..." in summary)

  ## Input Reports
  - plan
  - refactoring

  ## Output
  reportType: tests-review
```

### Step 6: code-review (code-reviewer)

```
subagent_type: code-reviewer
run_in_background: true
prompt: |
  TASK_ID: {TASK_ID}

  ## Task
  Review the refactored test code for quality issues.
  Apply your loaded skills (`code-review-checklist`, `design-assessment`).

  Classify findings as BLOCKING or NON-BLOCKING.

  Signal status:
  - "passed" = no blocking issues
  - "failed" = blocking issues found (include "BLOCKING: N issues" in summary)

  ## Input Reports
  - plan
  - refactoring
  - tests-review

  ## Output
  reportType: code-review
```

### Step 7: acceptance (acceptance-reviewer)

```
subagent_type: acceptance-reviewer
run_in_background: true
prompt: |
  TASK_ID: {TASK_ID}

  ## Task
  Verify acceptance criteria for test refactor:
  - Tests remain green (evidence via test runs)
  - No production code changed (evidence via diff checks)
  - Refactor scope stayed within the requested test scope
  - Test code quality improved (structure/readability/determinism)

  Signal status:
  - "passed" = all criteria met
  - "failed" = gaps found (include "PARTIAL: ..." in summary)

  ## Input Reports
  - requirements
  - plan
  - refactoring
  - tests-review
  - code-review

  ## Output
  reportType: acceptance
```

### Step 8: documentation (documentation-updater)

```
subagent_type: documentation-updater
run_in_background: true
prompt: |
  TASK_ID: {TASK_ID}

  ## Task
  Update only docs impacted by the refactor:
  - Test conventions
  - How to run tests
  - Fixture locations
  - etc.

  Do not change production code.
  After doc changes, run tests once.

  ## Input Reports
  - requirements
  - refactoring

  ## Output
  reportType: documentation
```

### Step 9: finalize (workflow-finalizer)

```
subagent_type: workflow-finalizer
run_in_background: true
prompt: |
  TASK_ID: {TASK_ID}

  ## Task
  Generate an executive summary of the completed tests refactor workflow.

  Read all available reports for this task and synthesize:
  - Overall outcome (success/partial/failed)
  - Key test improvements made
  - Open items/follow-ups (if any)
  - Files changed

  Keep the summary concise and focused on outcomes.

  ## Input Reports
  - requirements
  - codebase-analysis
  - plan
  - refactoring
  - tests-review
  - code-review
  - acceptance
  - documentation

  ## Output
  reportType: finalize
```

After the finalize signal is received, the orchestrator outputs the signal summary to the user and exits.
