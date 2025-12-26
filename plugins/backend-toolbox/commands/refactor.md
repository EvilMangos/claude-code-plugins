---
description: Refactor code in a given path (file or folder) with tests after each step; never modify test files. If no path is provided, scope is the entire codebase.
argument-hint: [ path ]
allowed-tools: Read, Edit, Write, Grep, Glob, Bash(git:*), Task, Skill, MCP
---

# Refactor Workflow (Background Agent Orchestration)

You are orchestrating a **refactor-only** workflow for this repository.

The user request is:

> $ARGUMENTS

The argument is an optional **path** to a file or folder. If no argument is provided, the scope is the **entire codebase**.

## Architecture: Workflow

This workflow drives all decisions:

1. **Orchestrator initializes task** with metadata
2. **The workflow determines the next step** based on current state
3. **Orchestrator executes the step** returned by the workflow
4. **Agent saves report and signal**
5. **Orchestrator queries for next step** - repeat until complete

**The orchestrator NEVER decides which step to run next. The workflow makes all routing decisions.**

## Task ID Generation

Before starting, generate a unique task ID for this workflow:

```
TASK_ID = refactor-{slug}-{timestamp}
```

Where:
- `slug`: URL-safe version of path or "codebase" (lowercase, hyphens, max 30 chars)
  - Example: "src/utils/helpers.ts" → `src-utils-helpers`
  - Example: (no path) → `codebase`
- `timestamp`: Unix timestamp in seconds (e.g., `1702834567`)

Example: `refactor-src-utils-helpers-1702834567`

## Hard constraints (non-negotiable)

1) **Do not modify test files** (read-only is fine).
   - You must NOT edit, create, delete, rename, or move any test file.
   - If a change would require updating tests, STOP and report that tests must be handled via the separate tests command.

   See `skills/test-best-practices/references/test-file-patterns.md` for complete test file identification patterns.
   Default patterns include: `/test/`, `/tests/`, `/__tests__/`, files containing `.spec.` or `.test.`, etc.

2) **Behavior-preserving refactor**
   - Do not change external behavior intentionally.
   - Prefer small, reversible steps.

3) **Tests after each step**
   - After **every refactor step** (each plan item that changes code), run tests with the smallest relevant scope.

## Preflight (main agent)

Before initializing the workflow, the main agent must:

1) Determine scope:
   - If `$ARGUMENTS` is empty: set scope to the repo root (`.`).
   - Else: set scope to `$ARGUMENTS`.

2) Verify the scope exists:
   - Use Glob on the chosen scope.
   - If it does not exist, STOP and report the path is invalid.

3) Establish baseline:
   - Run tests with a narrow scope relevant to the refactor (or the smallest reasonable default if broad scope).
   - If baseline is failing, STOP and report that refactor is blocked until tests are green.

## Orchestrator Loop

After initialization, the orchestrator runs this loop:

```
LOOP:
  1. Query for next step:
     - taskId: {TASK_ID}
     - Returns: { success, taskId, stepNumber, totalSteps, step?, complete? }

  2. IF complete == true:
     - Execute finalization
     - EXIT LOOP

  3. Launch the agent for the returned step (run_in_background: true)

  4. Wait for signal using `mcp__plugin_backend-toolbox_backend-toolbox-mcp__wait-signal`

  5. After signal received, proceed to step 1

  6. GOTO 1
END LOOP
```

**Critical Rules:**

1. **The orchestrator does NOT interpret signal status to decide next step. It always queries the workflow.**

2. **Always execute the step returned, even if that step was already executed before.**
   - The workflow may return the same step multiple times (e.g., `refactoring` after a failed `code-review`)
   - This is intentional: the workflow handles retry logic and gate failures internally
   - Do NOT skip a step because "it was already done"
   - Simply execute whatever step is returned, every time

3. **NEVER use TaskOutput to retrieve background agent results.**
   - Background agents communicate ONLY via MCP signals and reports
   - If you need agent results: use `mcp__plugin_backend-toolbox_backend-toolbox-mcp__get-report` tool, NOT TaskOutput

## Agent Output Instructions

**Always include these instructions in every agent prompt:**
```
## Workflow Context
TASK_ID: {TASK_ID}
SCOPE: {scope path or "entire codebase"}

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
   - "passed" = completed successfully, gate passed, no blocking issues
   - "failed" = needs iteration, has blocking issues, or error occurred
```

---

## Step Definitions

### initialize

Create task metadata:
- taskId: {TASK_ID}
- execution steps derive from Steps below

### Step 1: requirements (main agent captures scope)

The main agent (not a subagent) captures:
- Scope (path or entire codebase)
- Success criteria: behavior preserved, tests remain green, no test files changed
- Refactor goals: readability, structure, coupling, naming, duplication, error-handling hygiene

Save report and signal with reportType/signalType: "requirements"

### Step 2: codebase-analysis (codebase-analyzer)

```
subagent_type: codebase-analyzer
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}
  SCOPE: {scope}

  ## Task
  Analyze the codebase to understand existing patterns and conventions.
  This analysis will guide refactoring to ensure consistency.

  Focus on:
  - Code organization and module boundaries
  - Design patterns used in the affected areas
  - Naming conventions and style patterns
  - Existing abstractions and utilities

  ## Input Reports
  Retrieve (taskId={TASK_ID}):
  - reportType: "requirements"

  ## Output
  1. Save FULL report:
     - taskId: {TASK_ID}
     - reportType: "codebase-analysis"
     - content: <your codebase analysis report>
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "codebase-analysis"
     - content: { status: "passed", summary: "Codebase analysis complete" }
```

### Step 3: plan (plan-creator)

```
subagent_type: plan-creator
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}
  SCOPE: {scope}

  ## Task
  Create a small-step refactor plan (steps should be independently testable).
  For each step, include:
  - files to change (must exclude test files)
  - expected outcome
  - the smallest relevant test scope to use after that step

  Include a "test-file safety" note: how the plan avoids touching tests.
  If scope is the entire codebase: prioritize top 3-10 highest-value refactors.

  ## Input Reports
  Retrieve (taskId={TASK_ID}):
  - reportType: "requirements"
  - reportType: "codebase-analysis"

  ## Output
  1. Save FULL report:
     - taskId: {TASK_ID}
     - reportType: "plan"
     - content: <your refactor plan>
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "plan"
     - content: { status: "passed", summary: "Refactor plan created with N steps" }
```

### Step 4: refactoring (refactorer)

```
subagent_type: refactorer
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}
  SCOPE: {scope}

  ## Task
  Execute the refactor plan step-by-step.
  For each plan step:
  1) Make minimal behavior-preserving changes
  2) State what changed (files/functions) and why
  3) Run tests with the smallest relevant scope
  4) Check changed files with `git diff --name-only`
     - If any touched file matches test file patterns: revert and STOP

  If tests fail: fix the refactor (or revert) with minimal changes, re-run tests.

  Apply your loaded skills (`refactoring-patterns`, `design-assessment`, `design-patterns`).

  ## Input Reports
  Retrieve (taskId={TASK_ID}):
  Required:
  - reportType: "codebase-analysis"
  - reportType: "plan"
  Optional (contains feedback requiring additional fixes):
  - reportType: "code-review"
  - reportType: "acceptance"

  ## Output
  1. Save FULL report:
     - taskId: {TASK_ID}
     - reportType: "refactoring"
     - content: <your refactoring report with steps completed>
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "refactoring"
     - content: { status: "passed" or "failed", summary: "..." }
       - "passed" = all steps complete, tests green
       - "failed" = issues encountered (include details)
```

### Step 5: code-review (code-reviewer)

```
subagent_type: code-reviewer
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Review the refactored code for quality issues.
  Apply your loaded skills (`code-review-checklist`, `design-assessment`).

  Verify:
  - No test files were modified
  - Behavior is preserved
  - Code quality improved per stated goals
  - Changes follow codebase patterns

  Classify findings as BLOCKING or NON-BLOCKING.

  Return verdict in signal:
  - status: "passed" = no blocking issues
  - status: "failed" = blocking issues found (include "BLOCKING: N issues" in summary)

  ## Input Reports
  Retrieve (taskId={TASK_ID}):
  - reportType: "codebase-analysis"
  - reportType: "plan"
  - reportType: "refactoring"

  ## Output
  1. Save FULL report:
     - taskId: {TASK_ID}
     - reportType: "code-review"
     - content: <your code review report with verdict>
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "code-review"
     - content: { status: "passed" or "failed", summary: "..." }
```

### Step 6: acceptance (acceptance-reviewer)

```
subagent_type: acceptance-reviewer
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Verify acceptance criteria for refactor work:
  - Behavior preserved (as evidenced by tests)
  - No test files changed
  - Scope is reasonable for the provided scope
  - Code quality improved per stated goals

  Return verdict in signal:
  - status: "passed" = all criteria met
  - status: "failed" = gaps found (include "PARTIAL: ..." in summary)

  ## Input Reports
  Retrieve (taskId={TASK_ID}):
  - reportType: "requirements"
  - reportType: "plan"
  - reportType: "refactoring"
  - reportType: "code-review"

  ## Output
  1. Save FULL report:
     - taskId: {TASK_ID}
     - reportType: "acceptance"
     - content: <your acceptance review report with verdict>
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "acceptance"
     - content: { status: "passed" or "failed", summary: "..." }
```

### Step 7: documentation (documentation-updater)

```
subagent_type: documentation-updater
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Update documentation impacted by the refactor:
  - Do not modify test files
  - Keep doc changes minimal and accurate
  - Update only what is now misleading (paths, module names, usage examples, architecture notes)

  If doc updates include code changes, re-run tests once afterward.

  ## Input Reports
  Retrieve (taskId={TASK_ID}):
  - reportType: "requirements"
  - reportType: "plan"
  - reportType: "refactoring"

  ## Output
  1. Save FULL report:
     - taskId: {TASK_ID}
     - reportType: "documentation"
     - content: <your documentation update report>
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "documentation"
     - content: { status: "passed", summary: "Documentation updated" }
```

### finalize

The workflow is complete. Generate a final summary by:
- Retrieving full reports using the TASK_ID
- Update task metadata status to "completed"
