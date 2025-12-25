---
description: Develops a backend feature end-to-end using strict TDD with planning, test design, test review gate, implementation, QA, acceptance review, performance check, security check, refactoring, code review, and documentation updates.
argument-hint: [ feature-description ]
allowed-tools: Read, Edit, Write, Grep, Glob, Task, SlashCommand, Bash, AskUserQuestion, Skill, MCP
---

# Feature Development Workflow (Background Agent Orchestration)

You are orchestrating a multistep **TDD** feature workflow for this repository.

The user request is:

> $ARGUMENTS

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
TASK_ID = develop-feature-{slug}-{timestamp}
```

Where:
- `slug`: URL-safe version of feature description (lowercase, hyphens, max 30 chars)
  - Example: "User Authentication" → `user-authentication`
  - Example: "Add OAuth2 support for mobile apps" → `add-oauth2-support-for-mobile`
- `timestamp`: Unix timestamp in seconds (e.g., `1702834567`)

Example: `develop-feature-user-auth-1702834567`

## Orchestrator Loop

After initialization, the orchestrator runs this loop:

```
LOOP:
  1. Query for next step:
     - taskId: {TASK_ID}
     - Returns: { success, taskId, stepNumber, totalSteps, step?, complete? }
     - step can be a string ("plan") or array for parallel (["performance", "security"])

  2. IF complete == true:
     - Execute finalization
     - EXIT LOOP

  3. IF step is an array (parallel execution):
     - Launch ALL agents in parallel (single message, multiple Task tool calls)
     - Wait for ALL signals using wait-signal with array of signalTypes

  4. ELSE (step is a string):
     - Launch the single agent for the returned step
     - Wait for signal using wait-signal

  5. GOTO 1
END LOOP
```

**Critical Rules:**

1. **The orchestrator does NOT interpret signal status to decide next step. It always queries the workflow.**

2. **Always execute the step returned, even if that step was already executed before.**
   - The workflow may return the same step multiple times (e.g., `tests-design` after a failed `tests-review`)
   - This is intentional: the workflow handles retry logic and gate failures internally
   - Do NOT skip a step because "it was already done"
   - Do NOT question why a repeated step is being requested
   - Simply execute whatever step is returned, every time

## Agent Output Instructions

**Always include these instructions in every agent prompt:**
```
## Workflow Context
TASK_ID: {TASK_ID}

## Output
1. Save your FULL report:
   - taskId: {TASK_ID}
   - reportType: {report-type}  (e.g., "requirements", "plan", "implementation")
   - content: <your full report content>

2. Save your signal:
   - taskId: {TASK_ID}
   - signalType: {report-type}  (same as reportType)
   - content:
     - status: "passed" or "failed"
     - summary: {one sentence describing outcome}

   Status mapping:
   - "passed" = completed successfully, gate passed, no blocking issues
   - "failed" = needs iteration, has blocking issues, or error occurred
     (include details in summary: "PARTIAL: ...", "BLOCKING: ...", "ERROR: ...")
```

---

## Step Definitions

The following steps can be returned. Execute the corresponding agent when the step is returned.

### initialize

Create task metadata:
- taskId: {TASK_ID}
- execution steps derive from Steps below

### Step 1: requirements (business-analyst)

```
subagent_type: business-analyst
run_in_background: false
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Analyze the feature request and create specific requirements:
  - Restate the feature in your own words
  - Identify affected domains/packages
  - List ALL ambiguous points, unclear terms, or missing details
  - If ambiguities exist: ask ALL questions using AskUserQuestion tool
  - Review answers; if unclear or introduce new ambiguities, ask follow-ups
  - Derive behavioral requirements (REQ-1, REQ-2, etc.)

  ## Feature Request
  $ARGUMENTS

  ## Output
  1. Save FULL report:
     - taskId: {TASK_ID}
     - reportType: "requirements"
     - content: Include Feature Understanding, Affected Domains, Clarifications, Behavioral Requirements (REQ-1, REQ-2, etc.)
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "requirements"
     - content: { status: "passed", summary: "Requirements analysis complete with N requirements" }
```

### Step 2: plan (plan-creator)

```
subagent_type: plan-creator
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Create implementation and testing plan for the feature.

  ## Input Reports
  Retrieve (taskId={TASK_ID}):
  - reportType: "requirements"

  ## Output
  1. Save FULL report:
     - taskId: {TASK_ID}
     - reportType: "plan"
     - content: <your implementation and testing plan>
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "plan"
     - content: { status: "passed", summary: "Implementation plan created" }
```

### Step 3: tests-design (automation-qa)

```
subagent_type: automation-qa
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Design and write tests for the planned behavior (RED stage).
  - Normal paths
  - Edge cases
  - Error conditions

  After writing tests, run them to confirm they FAIL (RED).
  Use the narrowest test scope.

  ## Input Reports
  Retrieve (taskId={TASK_ID}):
  Required:
  - reportType: "requirements"
  - reportType: "plan"
  Optional (retrieve if available - contains feedback requiring new/updated tests):
  - reportType: "tests-review"
  - reportType: "stabilization"
  - reportType: "acceptance"
  - reportType: "code-review"

  ## Output
  1. Save FULL report:
     - taskId: {TASK_ID}
     - reportType: "tests-design"
     - content: <your test design report>
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "tests-design"
     - content: { status: "passed", summary: "N tests written, all failing as expected (RED)" }
```

### Step 4: tests-review (tests-reviewer)

```
subagent_type: tests-reviewer
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Review the tests for quality. Apply your loaded skills.
  Return verdict in signal:
  - status: "passed" = tests are ready for implementation
  - status: "failed" = tests need improvement (include "PARTIAL: ..." in summary)

  ## Input Reports
  Retrieve (taskId={TASK_ID}):
  - reportType: "requirements"
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

### Step 5: implementation (backend-developer)

```
subagent_type: backend-developer
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Implement the feature to make tests pass (GREEN stage).
  - Work in small incremental steps
  - Run tests after each step
  - Continue until all feature tests are GREEN

  ## Input Reports
  Retrieve (taskId={TASK_ID}):
  Required:
  - reportType: "requirements"
  - reportType: "plan"
  - reportType: "tests-design"
  Optional (retrieve if available - contains feedback requiring fixes):
  - reportType: "tests-review"
  - reportType: "stabilization"
  - reportType: "acceptance"
  - reportType: "performance"
  - reportType: "security"
  - reportType: "code-review"

  ## Output
  1. Save FULL report:
     - taskId: {TASK_ID}
     - reportType: "implementation"
     - content: <your implementation report>
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "implementation"
     - content: { status: "passed", summary: "Implementation complete, all tests passing" }
```

### Step 6: stabilization (automation-qa)

```
subagent_type: automation-qa
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Run broader test scope and assess stability:
  - Identify regression risks
  - Run package-level or broader tests
  - Report if additional tests are needed

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
     - content: <your stabilization report with verdict>
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "stabilization"
     - content: { status: "passed" or "failed", summary: "..." }
```

### Step 7: acceptance (acceptance-reviewer)

```
subagent_type: acceptance-reviewer
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Verify all requirements are met:
  - Check each REQ-N against implementation
  - Identify functional gaps

  Return verdict in signal:
  - status: "passed" = all requirements met
  - status: "failed" = gaps found (include "PARTIAL: ..." in summary)

  ## Input Reports
  Retrieve (taskId={TASK_ID}):
  - reportType: "requirements"
  - reportType: "plan"
  - reportType: "implementation"
  - reportType: "stabilization"

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

### Step 8: performance + security

Launch BOTH agents in parallel (single message, multiple Task tool calls):

**Agent A: performance-specialist**
```
subagent_type: performance-specialist
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Analyze the implementation for performance issues.
  Apply your loaded skills (`backend-performance`, `algorithm-efficiency`).
  Classify findings as BLOCKING or NON-BLOCKING.

  Return verdict in signal:
  - status: "passed" = no blocking issues
  - status: "failed" = blocking issues found (include "BLOCKING: ..." in summary)

  ## Input Reports
  Retrieve (taskId={TASK_ID}):
  - reportType: "implementation"

  ## Output
  1. Save FULL report:
     - taskId: {TASK_ID}
     - reportType: "performance"
     - content: <your performance analysis report with verdict>
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "performance"
     - content: { status: "passed" or "failed", summary: "..." }
```

**Agent B: application-security-specialist**
```
subagent_type: application-security-specialist
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Analyze the implementation for security vulnerabilities.
  Apply your loaded skill (`web-api-security`).
  Classify findings as BLOCKING or NON-BLOCKING.

  Return verdict in signal:
  - status: "passed" = no blocking issues
  - status: "failed" = blocking issues found (include "BLOCKING: ..." in summary)

  ## Input Reports
  Retrieve (taskId={TASK_ID}):
  - reportType: "implementation"

  ## Output
  1. Save FULL report:
     - taskId: {TASK_ID}
     - reportType: "security"
     - content: <your security analysis report with verdict>
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "security"
     - content: { status: "passed" or "failed", summary: "..." }
```

Wait for BOTH signals before querying for next step.

### Step 9: refactoring (refactorer)

```
subagent_type: refactorer
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Perform behavior-preserving cleanup.
  Apply your loaded skills (`refactoring-patterns`, `design-assessment`, `design-patterns`).
  Run tests after each refactor step.
  Record larger refactors as follow-up tasks, don't do them now.

  ## Input Reports
  Retrieve (taskId={TASK_ID}):
  Required:
  - reportType: "implementation"
  Optional (retrieve if available - contains structural issues to address):
  - reportType: "code-review"

  ## Output
  1. Save FULL report:
     - taskId: {TASK_ID}
     - reportType: "refactoring"
     - content: <your refactoring report>
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "refactoring"
     - content: { status: "passed", summary: "Refactoring complete, tests still passing" }
```

### Step 10: code-review (code-reviewer)

```
subagent_type: code-reviewer
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Review the code for quality issues.
  Apply your loaded skills (`code-review-checklist`, `design-assessment`).
  Classify findings as BLOCKING or NON-BLOCKING.
  For each BLOCKING issue, specify route:
  - "ROUTE: functional" → needs tests + implementation fix
  - "ROUTE: structural" → needs refactoring

  Return verdict in signal:
  - status: "passed" = no blocking issues
  - status: "failed" = blocking issues found (include "BLOCKING: N functional, M structural" in summary)

  ## Input Reports
  Retrieve (taskId={TASK_ID}):
  - reportType: "implementation"
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

### Step 11: documentation (documentation-updater)

```
subagent_type: documentation-updater
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Update documentation impacted by the change:
  - README usage examples
  - Configuration/env var references
  - Architecture notes
  - Runbooks

  Keep changes minimal and tied to implemented behavior.

  ## Input Reports
  Retrieve (taskId={TASK_ID}):
  - reportType: "requirements"
  - reportType: "plan"
  - reportType: "implementation"

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

---

