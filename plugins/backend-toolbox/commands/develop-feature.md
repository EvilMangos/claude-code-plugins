---
description: Develops a backend feature end-to-end using strict TDD with planning, test design, test review gate, implementation, QA, acceptance review, performance check, security check, refactoring, code review, and documentation updates.
argument-hint: [ feature-description ]
allowed-tools: Read, Edit, Write, Grep, Glob, Task, SlashCommand, Bash, AskUserQuestion
---

# Feature Development Workflow (Background Agent Orchestration)

You are orchestrating a multistep **TDD** feature workflow for this repository.

The user request is:

> $ARGUMENTS

## Architecture: Background Agents with File-Based Context

This workflow uses background agents to minimize context window usage:

1. **Each agent runs in background** (`run_in_background: true`)
2. **Each agent writes full report to file** (`{WORKFLOW_DIR}/{step}-{name}.md`)
3. **Each agent returns brief status** (STATUS, FILE, SUMMARY, NEXT_INPUT)
4. **Orchestrator only sees status** - full context stays in files
5. **Next agent reads previous files** - gets context from disk

**Critical: Always include these instructions in every agent prompt:**
```
You MUST use the workflow-report-format skill for output formatting.

## Workflow Directory
WORKFLOW_DIR: {WORKFLOW_DIR}

Write your FULL report to: {WORKFLOW_DIR}/{step}-{name}.md
Return ONLY the brief orchestrator response (max 10 lines) as your final output.
```

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

Set the workflow directory:
```
WORKFLOW_DIR = .workflow/{TASK_ID}
```

## Workflow State Directory

Initialize the workflow directory with the generated task ID:

```bash
mkdir -p {WORKFLOW_DIR}/loop-iterations
```

Create `{WORKFLOW_DIR}/metadata.json`:
```json
{
  "taskId": "{TASK_ID}",
  "command": "develop-feature",
  "feature": "$ARGUMENTS",
  "started": "{ISO timestamp}",
  "currentStep": 1,
  "status": "in_progress"
}
```

## Agent Invocation Pattern

For EVERY agent, use this pattern:

```
Task tool:
  subagent_type: {agent-name}
  run_in_background: true
  prompt: |
    You MUST use the workflow-report-format skill.

    ## Workflow Directory
    WORKFLOW_DIR: {WORKFLOW_DIR}

    ## Your Task
    {task description}

    ## Input Files to Read
    {list of {WORKFLOW_DIR}/*.md files to read}

    ## Output
    1. Write FULL report to: {WORKFLOW_DIR}/{step}-{name}.md
    2. Return ONLY this format:
       STATUS: {PASS|PARTIAL|FAIL|DONE}
       FILE: {WORKFLOW_DIR}/{step}-{name}.md
       SUMMARY: {one sentence}
       NEXT_INPUT: {comma-separated file list for next agent}
       ---
       {2-5 bullet key points}
```

Then immediately call `TaskOutput` with `block: true` to wait for completion.

Parse the STATUS from the response to decide next action.

---

## Workflow Steps

### Step 0: Initialize

1. Generate TASK_ID (see "Task ID Generation" above)
2. Set `WORKFLOW_DIR = .workflow/{TASK_ID}`
3. Create `{WORKFLOW_DIR}/` directory and `{WORKFLOW_DIR}/loop-iterations/`
4. Create `metadata.json`

### Step 1: Requirements Analysis (business-analyst)

Launch in background:
```
subagent_type: business-analyst
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Workflow Directory
  WORKFLOW_DIR: {WORKFLOW_DIR}

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
  1. Write FULL report to: {WORKFLOW_DIR}/requirements.md
     Include:
     - Feature Understanding (your restatement)
     - Affected Domains/Components
     - Clarifications (Q&A pairs if any)
     - Behavioral Requirements (REQ-1, REQ-2, etc.)
  2. Return brief status only
```

Wait with `TaskOutput(block: true)`.

### Step 2: Planning (plan-creator)

Launch in background:
```
subagent_type: plan-creator
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Workflow Directory
  WORKFLOW_DIR: {WORKFLOW_DIR}

  ## Task
  Create implementation and testing plan for the feature.

  ## Input
  Read: {WORKFLOW_DIR}/requirements.md

  ## Output
  1. Write FULL report to: {WORKFLOW_DIR}/plan.md
  2. Return brief status only
```

Wait with `TaskOutput(block: true)`.

### Step 3: Test Design - RED Stage (automation-qa)

Launch in background:
```
subagent_type: automation-qa
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Workflow Directory
  WORKFLOW_DIR: {WORKFLOW_DIR}

  ## Task
  Design and write tests for the planned behavior (RED stage).
  - Normal paths
  - Edge cases
  - Error conditions

  After writing tests, run them to confirm they FAIL (RED).
  Use /run-tests with the narrowest scope.

  ## Input
  Required: {WORKFLOW_DIR}/requirements.md, {WORKFLOW_DIR}/plan.md
  Optional (read if present - contains reviewer feedback requiring new/updated tests):
  - {WORKFLOW_DIR}/tests-review.md
  - {WORKFLOW_DIR}/stabilization.md
  - {WORKFLOW_DIR}/acceptance.md
  - {WORKFLOW_DIR}/code-review.md

  ## Output
  1. Write FULL report to: {WORKFLOW_DIR}/tests-design.md
  2. Return brief status only
```

Wait with `TaskOutput(block: true)`.

### Step 4: Test Quality Gate (tests-reviewer)

Launch in background:
```
subagent_type: tests-reviewer
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Workflow Directory
  WORKFLOW_DIR: {WORKFLOW_DIR}

  ## Task
  Review the tests for quality. Apply your loaded skills.
  Return verdict: PASS / PARTIAL / FAIL

  ## Input
  Read: {WORKFLOW_DIR}/requirements.md, {WORKFLOW_DIR}/plan.md, {WORKFLOW_DIR}/tests-design.md

  ## Output
  1. Write FULL report to: {WORKFLOW_DIR}/tests-review.md
  2. Return brief status only
```

Wait with `TaskOutput(block: true)`.

**Loop Logic:**
- If STATUS is PASS → proceed to Step 5
- If STATUS is PARTIAL or FAIL → go to Step 3, then re-run Step 4
- Do NOT proceed to implementation until PASS

### Step 5: Implementation - GREEN Stage (backend-developer)

Launch in background:
```
subagent_type: backend-developer
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Workflow Directory
  WORKFLOW_DIR: {WORKFLOW_DIR}

  ## Task
  Implement the feature to make tests pass (GREEN stage).
  - Work in small incremental steps
  - Run /run-tests after each step
  - Continue until all feature tests are GREEN

  ## Input
  Required: {WORKFLOW_DIR}/requirements.md, {WORKFLOW_DIR}/plan.md, {WORKFLOW_DIR}/tests-design.md
  Optional (read if present - contains reviewer feedback requiring fixes):
  - {WORKFLOW_DIR}/tests-review.md
  - {WORKFLOW_DIR}/stabilization.md
  - {WORKFLOW_DIR}/acceptance.md
  - {WORKFLOW_DIR}/performance.md
  - {WORKFLOW_DIR}/security.md
  - {WORKFLOW_DIR}/code-review.md

  ## Output
  1. Write FULL report to: {WORKFLOW_DIR}/implementation.md
  2. Return brief status only
```

Wait with `TaskOutput(block: true)`.

### Step 6: Stabilization Gate (automation-qa)

Launch in background:
```
subagent_type: automation-qa
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Workflow Directory
  WORKFLOW_DIR: {WORKFLOW_DIR}

  ## Task
  Run broader test scope and assess stability:
  - Identify regression risks
  - Run package-level or broader /run-tests
  - Report if additional tests are needed

  Return verdict: PASS / PARTIAL / FAIL

  ## Input
  Read: {WORKFLOW_DIR}/requirements.md, {WORKFLOW_DIR}/plan.md, {WORKFLOW_DIR}/implementation.md

  ## Output
  1. Write FULL report to: {WORKFLOW_DIR}/stabilization.md
  2. Return brief status only
```

Wait with `TaskOutput(block: true)`.

**Loop Logic (TDD):**
- If STATUS is PASS → proceed to Step 7
- If STATUS is PARTIAL or FAIL:
  1. Go to Step 3 (automation-qa writes/updates tests for issues - RED)
  2. Go to Step 5 (backend-developer fixes - GREEN)
  3. Re-run Step 6
  4. Repeat until PASS

### Step 7: Acceptance Review (acceptance-reviewer)

Launch in background:
```
subagent_type: acceptance-reviewer
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Workflow Directory
  WORKFLOW_DIR: {WORKFLOW_DIR}

  ## Task
  Verify all requirements are met:
  - Check each REQ-N against implementation
  - Identify functional gaps

  Return verdict: PASS / PARTIAL / FAIL

  ## Input
  Read: {WORKFLOW_DIR}/requirements.md, {WORKFLOW_DIR}/plan.md, {WORKFLOW_DIR}/implementation.md, {WORKFLOW_DIR}/stabilization.md

  ## Output
  1. Write FULL report to: {WORKFLOW_DIR}/acceptance.md
  2. Return brief status only
```

Wait with `TaskOutput(block: true)`.

**Loop Logic (TDD):**
- If STATUS is PASS → proceed to Step 8
- If STATUS is PARTIAL or FAIL:
  1. Go to Step 3 (automation-qa adds tests for gaps - RED)
  2. Go to Step 5 (backend-developer implements - GREEN)
  3. Re-run Step 7
  4. Repeat until PASS

### Step 8: Performance & Security Check (Parallel)

Launch BOTH agents IN PARALLEL (single message, multiple Task tool calls):

**First Task call (performance-specialist):**
```
subagent_type: performance-specialist
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Workflow Directory
  WORKFLOW_DIR: {WORKFLOW_DIR}

  ## Task
  Analyze the implementation for performance issues.
  Apply your loaded skills (`backend-performance`, `algorithm-efficiency`).
  Classify findings as BLOCKING or NON-BLOCKING.
  Return verdict: PASS / PARTIAL / FAIL

  ## Input
  Required: {WORKFLOW_DIR}/implementation.md

  ## Output
  1. Write FULL report to: {WORKFLOW_DIR}/performance.md
  2. Return brief status only
```

**Second Task call (application-security-specialist) - SAME MESSAGE:**
```
subagent_type: application-security-specialist
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Workflow Directory
  WORKFLOW_DIR: {WORKFLOW_DIR}

  ## Task
  Analyze the implementation for security vulnerabilities.
  Apply your loaded skill (`web-api-security`).
  Classify findings as BLOCKING or NON-BLOCKING.
  Return verdict: PASS / PARTIAL / FAIL

  ## Input
  Required: {WORKFLOW_DIR}/implementation.md

  ## Output
  1. Write FULL report to: {WORKFLOW_DIR}/security.md
  2. Return brief status only
```

Wait for BOTH using `TaskOutput(block: true)` for each task ID.

**Loop Logic:**
- If BOTH statuses are PASS → proceed to Step 9
- If EITHER status is PARTIAL or FAIL with BLOCKING issues:
  1. Go to Step 5 (backend-developer fixes BLOCKING issues from both reviews)
  2. Re-run Step 8
  3. Repeat until BOTH PASS or only NON-BLOCKING remain

**Loop Exit:** BOTH statuses are PASS, only NON-BLOCKING remain, or iteration > 5 (max)

### Step 9: Refactoring (refactorer)

Launch in background:
```
subagent_type: refactorer
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Workflow Directory
  WORKFLOW_DIR: {WORKFLOW_DIR}

  ## Task
  Perform behavior-preserving cleanup.
  Apply your loaded skills (`refactoring-patterns`, `design-assessment`, `design-patterns`).
  Run /run-tests after each refactor step.
  Record larger refactors as follow-up tasks, don't do them now.

  ## Input
  Required: {WORKFLOW_DIR}/implementation.md
  Optional (read if present - contains structural issues to address):
  - {WORKFLOW_DIR}/code-review.md

  ## Output
  1. Write FULL report to: {WORKFLOW_DIR}/refactoring.md
  2. Return brief status only
```

Wait with `TaskOutput(block: true)`.

### Step 10: Code Review (code-reviewer)

Launch in background:
```
subagent_type: code-reviewer
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Workflow Directory
  WORKFLOW_DIR: {WORKFLOW_DIR}

  ## Task
  Review the code for quality issues.
  Apply your loaded skills (`code-review-checklist`, `design-assessment`).
  Classify findings as BLOCKING or NON-BLOCKING.
  For each BLOCKING issue, specify route:
  - "ROUTE: functional" → needs tests + implementation fix
  - "ROUTE: structural" → needs refactoring

  Return verdict: PASS / PARTIAL / FAIL

  ## Input
  Required: {WORKFLOW_DIR}/implementation.md, {WORKFLOW_DIR}/refactoring.md

  ## Output
  1. Write FULL report to: {WORKFLOW_DIR}/code-review.md
  2. Return brief status only
```

Wait with `TaskOutput(block: true)`.

**Loop Logic (with routing):**
- If STATUS is PASS → proceed to Step 11
- If STATUS is PARTIAL or FAIL with BLOCKING issues:
  - Parse BLOCKING issues by route from code-review.md
  - **For functional issues (ROUTE: functional):**
    1. Go to Step 3 (automation-qa adds/updates tests - RED)
    2. Go to Step 5 (backend-developer fixes - GREEN)
  - **For structural issues (ROUTE: structural):**
    1. Go to Step 9 (refactorer addresses structural issues)
  - Re-run Step 10
  - Repeat until PASS or only NON-BLOCKING remain

**Loop Exit:** STATUS is PASS, only NON-BLOCKING remain, iteration > 5 (max), or user accepts trade-offs

### Step 11: Documentation (documentation-updater)

Launch in background:
```
subagent_type: documentation-updater
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Workflow Directory
  WORKFLOW_DIR: {WORKFLOW_DIR}

  ## Task
  Update documentation impacted by the change:
  - README usage examples
  - Configuration/env var references
  - Architecture notes
  - Runbooks

  Keep changes minimal and tied to implemented behavior.

  ## Input
  Read: {WORKFLOW_DIR}/requirements.md, {WORKFLOW_DIR}/plan.md, {WORKFLOW_DIR}/implementation.md

  ## Output
  1. Write FULL report to: {WORKFLOW_DIR}/documentation.md
  2. Return brief status only
```

Wait with `TaskOutput(block: true)`.

### Step 12: Finalize

Update `{WORKFLOW_DIR}/metadata.json`:
```json
{
  "taskId": "{TASK_ID}",
  "command": "develop-feature",
  "feature": "$ARGUMENTS",
  "started": "{original start timestamp}",
  "currentStep": 12,
  "status": "completed",
  "completedAt": "{ISO timestamp}"
}
```

The workflow-completion hook will generate the final summary by reading `{WORKFLOW_DIR}/` files.

---

## Non-Negotiable Constraints

1. **TDD is mandatory:**
   - Tests before implementation
   - Tests reviewed (PASS) before implementation begins
   - /run-tests after every implementation or refactor step

2. **Background agents only:**
   - All agents MUST run with `run_in_background: true`
   - Always wait with `TaskOutput(block: true)` before next step

3. **File-based context:**
   - Agents write full reports to files in `{WORKFLOW_DIR}/`
   - Agents return only brief status to orchestrator
   - Next agent reads previous agent's files

4. **No scope creep:**
   - Do not introduce features beyond $ARGUMENTS

5. **Skill usage:**
   - Every agent prompt MUST mention `workflow-report-format` skill
   - Every agent prompt MUST include `WORKFLOW_DIR: {WORKFLOW_DIR}`

6. **Verify output files:**
   - After each `TaskOutput`, verify the reported FILE exists
   - If file missing: HALT and report error to user

7. **Handle STATUS: ERROR:**
   - If any agent returns `STATUS: ERROR`, HALT the workflow immediately
   - Do NOT proceed to the next step
   - Do NOT retry the failed agent
   - Report to user with details from the error response

8. **Missing input file protocol:**
   - If an agent cannot find a required input file:
     1. Agent lists `{WORKFLOW_DIR}/` directory contents
     2. Agent attempts to identify alternative file (name variations)
     3. If found: use it and log warning in Handoff Notes
     4. If not found: return `STATUS: ERROR` with file listing
   - Orchestrator halts and reports to user

9. **Write failure protocol:**
   - If an agent cannot write its output file:
     1. Agent attempts recovery (mkdir -p {WORKFLOW_DIR}/loop-iterations)
     2. If still fails: return `STATUS: ERROR` with error details
     3. NEVER return DONE/PASS if file was not written
   - Orchestrator halts and reports to user with recovery steps

10. **Task isolation:**
    - Each workflow MUST use its own unique subdirectory under `.workflow/`
    - Never write to `.workflow/` root
    - This allows multiple workflows to run concurrently
