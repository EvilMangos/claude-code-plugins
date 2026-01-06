---
description: Refactor code in a given path (file or folder) with tests updated to match. If no path is provided, scope is the entire codebase.
argument-hint: [ path ] [ instructions ]
allowed-tools: Read, Edit, Write, Grep, Glob, Bash(git:*), Task, Skill, MCP
---

# Refactor Workflow (Background Agent Orchestration)

You are orchestrating a **refactor-only** workflow for this repository.

## Arguments

| Arg | Value | Description |
|-----|-------|-------------|
| `$1` | `$1` | Path to file or folder. If empty or `-`, scope is **entire codebase**. |
| `$2` | `$2` | Specific refactoring instructions/focus areas. |

Examples:
- `/refactor` → scope: entire codebase, no instructions
- `/refactor src/utils` → scope: src/utils, no instructions
- `/refactor - "reduce duplication in helper functions"` → entire codebase, with instructions
- `/refactor src/utils "extract common patterns"` → src/utils, with instructions

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
TASK_ID = refactor-{slug}-{timestamp}
```

Where:
- `slug`: URL-safe version of path or "codebase" (lowercase, hyphens, max 30 chars)
  - Example: "src/utils/helpers.ts" → `src-utils-helpers`
  - Example: (no path) → `codebase`
- `timestamp`: Unix timestamp in seconds (e.g., `1702834567`)

Example: `refactor-src-utils-helpers-1702834567`

## Hard constraints (non-negotiable)

1) **No backward compatibility hacks**
   - Do NOT create shims, re-exports, aliases, or wrapper functions to maintain old interfaces
   - Do NOT rename unused variables with `_` prefix just to suppress warnings
   - Do NOT add `// removed` or `// deprecated` comments for deleted code
   - When you rename/move/delete something, update all usages directly—never create a compatibility layer
   - If something is unused after refactoring, delete it completely

2) **Behavior-preserving refactor**
   - Do not change external behavior intentionally.
   - Prefer small, reversible steps.

3) **Separation of concerns**
   - The **refactorer** modifies production code only (no test files)
   - The **automation-qa** updates tests to match the refactored code
   - This ensures clean separation and proper test expertise

## Preflight (main agent)

Before initializing the workflow, the main agent must:

1) Determine scope and instructions:
   - If `$1` is empty or `-`: set scope to the repo root (`.`).
   - Else: set scope to `$1`.
   - Set instructions to `$2` (may be empty).

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
   - The workflow may return the same step multiple times (e.g., `refactoring` after a failed `code-review`)
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
- executionSteps: `["requirements", "codebase-analysis", "plan", "refactoring", "test-refactoring", "code-review", "acceptance", "documentation", "finalize"]`

### Step 1: requirements (main agent captures scope)

The main agent (not a subagent) captures:
- Scope (path or entire codebase)
- Instructions (user-provided refactoring focus, if any)
- Success criteria: behavior preserved, tests updated and green, no backward compatibility code
- Refactor goals: readability, structure, coupling, naming, duplication, error-handling hygiene
  - If instructions provided: prioritize user's specified focus areas

Save report and signal with reportType/signalType: "requirements"

### Step 2: codebase-analysis (codebase-analyzer)

```
subagent_type: codebase-analyzer
run_in_background: true
prompt: |
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
  INSTRUCTIONS: {instructions}

  ## Task
  Create a small-step refactor plan (steps should be independently testable).
  For each step, include:
  - production files to change (test updates handled separately by automation-qa)
  - expected outcome
  - anticipated test impacts (what tests may need updating)

  If scope is the entire codebase: prioritize top 3-10 highest-value refactors.

  **If INSTRUCTIONS provided**: Use them to guide priorities and focus areas.
  The plan should directly address the user's specified refactoring goals.

  **Important**: Plan for clean refactoring without backward compatibility hacks.
  If renaming/moving/deleting, plan to update all usages directly.

  ## Input Reports
  - requirements
  - codebase-analysis

  ## Output
  reportType: plan
```

### Step 4: refactoring (refactorer)

```
subagent_type: refactorer
run_in_background: true
prompt: |
  TASK_ID: {TASK_ID}
  SCOPE: {scope}

  ## Task
  Execute the refactor plan step-by-step.
  For each plan step:
  1) Make clean, behavior-preserving changes to production code
  2) State what changed (files/functions) and why
  3) Do NOT modify test files—automation-qa handles that next

  **Critical: No backward compatibility hacks!**
  - Do NOT create shims, re-exports, or aliases for old names
  - Do NOT rename unused vars with `_` prefix to suppress warnings
  - When renaming/moving/deleting, update all production code usages directly
  - If something becomes unused, delete it completely

  Tests may fail after your changes—that's expected. The automation-qa step
  will update tests to match your refactored code.

  Apply your loaded skills (`refactoring-patterns`, `design-assessment`, `design-patterns`).

  ## Input Reports
  Required:
  - codebase-analysis
  - plan
  Optional (contains feedback requiring additional fixes):
  - code-review
  - acceptance

  ## Output
  reportType: refactoring
```

### Step 5: test-refactoring (automation-qa)

```
subagent_type: automation-qa
run_in_background: true
prompt: |
  TASK_ID: {TASK_ID}
  SCOPE: {scope}

  ## Task
  Update tests to match the refactored production code.

  1) Run tests to identify failures caused by refactoring
  2) For each failing test:
     - Update imports, function names, paths to match refactored code
     - Adjust test assertions if internal structure changed
     - Preserve test intent and coverage—only adapt to new structure
  3) Run tests again to verify all pass
  4) If new code paths were added, consider adding minimal test coverage

  **Important**:
  - Do NOT change test logic or reduce coverage
  - Only adapt tests to the new code structure
  - Apply your loaded skills (`test-best-practices`)

  ## Input Reports
  Required:
  - plan
  - refactoring

  ## Output
  reportType: test-refactoring
```

### Step 6: code-review (code-reviewer)

```
subagent_type: code-reviewer
run_in_background: true
prompt: |
  TASK_ID: {TASK_ID}

  ## Task
  Review the refactored code and updated tests for quality issues.
  Apply your loaded skills (`code-review-checklist`, `design-assessment`).

  Verify:
  - No backward compatibility hacks (shims, re-exports, aliases)
  - Behavior is preserved
  - Code quality improved per stated goals
  - Changes follow codebase patterns
  - Tests properly updated to match refactored code

  Return verdict in signal:
  - status: "passed" = no issues found
  - status: "failed" = issues found (include "ISSUES: N" in summary)

  ## Input Reports
  - codebase-analysis
  - plan
  - refactoring
  - test-refactoring

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
  Verify acceptance criteria for refactor work:
  - Behavior preserved (as evidenced by tests passing)
  - No backward compatibility hacks in production code
  - Tests properly updated to match refactored code
  - Scope is reasonable for the provided scope
  - Code quality improved per stated goals

  Return verdict in signal:
  - status: "passed" = all criteria met
  - status: "failed" = gaps found (include "PARTIAL: ..." in summary)

  ## Input Reports
  - requirements
  - plan
  - refactoring
  - test-refactoring
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
  Update documentation impacted by the refactor:
  - Keep doc changes minimal and accurate
  - Update only what is now misleading (paths, module names, usage examples, architecture notes)

  If doc updates include code changes, re-run tests once afterward.

  ## Input Reports
  - requirements
  - plan
  - refactoring
  - test-refactoring

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
  Generate an executive summary of the completed refactor workflow.

  Read all available reports for this task and synthesize:
  - Overall outcome (success/partial/failed)
  - Key refactoring improvements made
  - Open items/follow-ups (if any)
  - Files changed

  Keep the summary concise and focused on outcomes.

  ## Output
  reportType: finalize
```

After the finalize signal is received, the orchestrator outputs the signal summary to the user and exits.
