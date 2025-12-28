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
  1. Get next step (returns: stepNumber, totalSteps, step, complete)
     - step can be a string ("plan") or array for parallel (["performance", "security"])

  2. IF complete == true:
     - Output final signal summary to user
     - EXIT LOOP

  3. IF step is an array (parallel execution):
     - Launch ALL agents in parallel (single message, multiple Task tool calls)
     - Wait for all signals (comma-separated types)

  4. ELSE (step is a string):
     - Launch the single agent for the returned step
     - Wait for signal

  5. GOTO 1
END LOOP
```

**IMPORTANT: Always wait for signal after every step**
- Waiting for signal advances the workflow to the next step
- For background agents: polls until signal appears
- For foreground agents: signal already saved, returns immediately
- Skipping wait causes workflow to get stuck on the same step

**Critical Rules:**

1. **The orchestrator does NOT interpret signal status to decide next step. It always queries the workflow.**

2. **Always execute the step returned, even if that step was already executed before.**
   - The workflow may return the same step multiple times (e.g., `tests-design` after a failed `tests-review`)
   - This is intentional: the workflow handles retry logic and gate failures internally
   - Do NOT skip a step because "it was already done"
   - Do NOT question why a repeated step is being requested
   - Simply execute whatever step is returned, every time

3. **NEVER use TaskOutput to retrieve background agent results.**
   - Background agents communicate ONLY via signals and reports
   - Using TaskOutput pulls verbose agent output (tool calls, file reads, etc.) into the main context
   - This wastes context window and defeats the purpose of background execution
   - If you need agent results: use get-report script, NOT TaskOutput
   - The signal summary provides enough info for the orchestrator to proceed

---

## Step Definitions

The following steps can be returned. Execute the corresponding agent when the step is returned.

### initialize

Create task metadata:
- taskId: {TASK_ID}
- executionSteps: `["requirements", "codebase-analysis", "plan", "tests-design", "tests-review", "implementation", "stabilization", "acceptance", ["performance", "security"], "refactoring", "code-review", "documentation", "finalize"]`

### Step 1: requirements (business-analyst)

```
subagent_type: business-analyst
run_in_background: false
prompt: |
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
  reportType: requirements
```

### Step 2: codebase-analysis (codebase-analyzer)

```
subagent_type: codebase-analyzer
run_in_background: true
prompt: |
  TASK_ID: {TASK_ID}

  ## Task
  Analyze the codebase to identify existing practices, patterns, and conventions.
  This analysis will guide implementation to ensure consistency with the codebase.

  Focus on:
  - Files/directory structure
  - DI/IoC container patterns
  - Error handling conventions
  - Logging patterns
  - Testing structure and patterns
  - API/endpoint conventions
  - Database access patterns
  - Configuration management
  - Common utilities and helpers

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
  Create implementation and testing plan for the feature.
  Use the codebase analysis to ensure the plan follows existing patterns.

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
  Design and write tests for the planned behavior (RED stage).
  - Normal paths
  - Edge cases
  - Error conditions

  After writing tests, run them to confirm they FAIL (RED).
  Use the narrowest test scope.

  ## Input Reports
  Required:
  - requirements
  - plan
  Optional (contains feedback requiring new/updated tests):
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
  Review the tests for quality. Apply your loaded skills.
  Return verdict in signal:
  - status: "passed" = tests are ready for implementation
  - status: "failed" = tests need improvement (include "PARTIAL: ..." in summary)

  ## Input Reports
  - requirements
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
  Implement the feature to make tests pass (GREEN stage).
  - Work in small incremental steps
  - Run tests after each step
  - Continue until all feature tests are GREEN
  - Follow patterns identified in codebase-analysis

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
  - performance
  - security
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
  - Identify regression risks
  - Run package-level or broader tests
  - Report if additional tests are needed

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
  Verify all requirements are met:
  - Check each REQ-N against implementation
  - Identify functional gaps

  Return verdict in signal:
  - status: "passed" = all requirements met
  - status: "failed" = gaps found (include "PARTIAL: ..." in summary)

  ## Input Reports
  - requirements
  - plan
  - implementation
  - stabilization

  ## Output
  reportType: acceptance
```

### Step 9: performance + security

Launch BOTH agents in parallel (single message, multiple Task tool calls):

**Agent A: performance-specialist**
```
subagent_type: performance-specialist
run_in_background: true
prompt: |
  TASK_ID: {TASK_ID}

  ## Task
  Analyze the implementation for performance issues.
  Apply your loaded skills (`backend-performance`, `algorithm-efficiency`).
  Consider codebase patterns (caching, connection pooling, etc.) when analyzing.

  Return verdict in signal:
  - status: "passed" = no issues found
  - status: "failed" = issues found (include "ISSUES: N" in summary)

  ## Input Reports
  - codebase-analysis
  - implementation

  ## Output
  reportType: performance
```

**Agent B: application-security-specialist**
```
subagent_type: application-security-specialist
run_in_background: true
prompt: |
  TASK_ID: {TASK_ID}

  ## Task
  Analyze the implementation for security vulnerabilities.
  Apply your loaded skill (`web-api-security`).
  Consider codebase security patterns (auth, validation, error handling) when analyzing.

  Return verdict in signal:
  - status: "passed" = no issues found
  - status: "failed" = issues found (include "ISSUES: N" in summary)

  ## Input Reports
  - codebase-analysis
  - implementation

  ## Output
  reportType: security
```

Wait for BOTH signals before querying for next step.

### Step 10: refactoring (refactorer)

```
subagent_type: refactorer
run_in_background: true
prompt: |
  TASK_ID: {TASK_ID}

  ## Task
  Perform behavior-preserving cleanup.
  Apply your loaded skills (`refactoring-patterns`, `design-assessment`, `design-patterns`).
  Run tests after each refactor step.
  Record larger refactors as follow-up tasks, don't do them now.
  Ensure refactored code follows patterns from codebase-analysis.

  ## Input Reports
  Required:
  - codebase-analysis
  - implementation
  Optional (contains structural issues to address):
  - code-review

  ## Output
  reportType: refactoring
```

### Step 11: code-review (code-reviewer)

```
subagent_type: code-reviewer
run_in_background: true
prompt: |
  TASK_ID: {TASK_ID}

  ## Task
  Review the code for quality issues.
  Apply your loaded skills (`code-review-checklist`, `design-assessment`).
  Check that implementation follows patterns from codebase-analysis.
  For each issue, specify route:
  - "ROUTE: functional" → needs tests + implementation fix
  - "ROUTE: structural" → needs refactoring

  Return verdict in signal:
  - status: "passed" = no issues found
  - status: "failed" = issues found (include "ISSUES: N functional, M structural" in summary)

  ## Input Reports
  - codebase-analysis
  - implementation
  - refactoring

  ## Output
  reportType: code-review
```

### Step 12: documentation (documentation-updater)

```
subagent_type: documentation-updater
run_in_background: true
prompt: |
  TASK_ID: {TASK_ID}

  ## Task
  Update documentation impacted by the change:
  - README usage examples
  - Configuration/env var references
  - Architecture notes
  - Runbooks

  Keep changes minimal and tied to implemented behavior.

  ## Input Reports
  - requirements
  - plan
  - implementation

  ## Output
  reportType: documentation
```

### Step 13: finalize (workflow-finalizer)

```
subagent_type: workflow-finalizer
run_in_background: true
prompt: |
  TASK_ID: {TASK_ID}

  ## Task
  Generate an executive summary of the completed workflow.

  Read all available reports for this task and synthesize:
  - Overall outcome (success/partial/failed)
  - Key accomplishments (3-5 bullets)
  - Important decisions made
  - Open items/follow-ups (if any)
  - Files changed

  Keep the summary concise and focused on outcomes.

  ## Output
  reportType: finalize
```

After the finalize signal is received, the orchestrator outputs the signal summary to the user and exits.

---

