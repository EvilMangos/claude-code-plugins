---
description: Develops a backend feature end-to-end using strict TDD with planning, test design, test review gate, implementation, QA, acceptance review, performance check, security check, refactoring, code review, and documentation updates.
argument-hint: [ feature-description ]
allowed-tools: Read, Edit, Write, Grep, Glob, Task, SlashCommand, Bash, AskUserQuestion
---

# Feature Development Workflow (Background Agent Orchestration)

You are orchestrating a multistep **TDD** feature workflow for this repository.

The user request is:

> $ARGUMENTS

## Architecture: Background Agents with MCP-Based Reports

This workflow uses background agents to minimize context window usage:

1. **Each agent runs in background** (`run_in_background: true`)
2. **Each agent saves full report to MCP storage** (using `save-report` tool)
3. **Each agent writes short status to signal file** (`{WORKFLOW_DIR}/{name}-report.md`)
4. **Orchestrator polls for signal file** - no TaskOutput needed
5. **Orchestrator reads only the short report** - full context stays in MCP storage
6. **Next agent retrieves previous full reports from MCP** (using `get-report` tool)

**Critical: Always include these instructions in every agent prompt:**
```
## Workflow Context
TASK_ID: {TASK_ID}
WORKFLOW_DIR: {WORKFLOW_DIR}

## Output
1. Save your FULL report to MCP storage:
   - taskId: {TASK_ID}
   - reportType: {report-type}  (e.g., "requirements", "plan", "implementation")
   - content: <your full report content>

2. Write your SHORT status report to file: {WORKFLOW_DIR}/{name}-report.md
   The short report MUST contain ONLY:
   STATUS: {PASS|PARTIAL|FAIL|DONE|ERROR}
   REPORT_TYPE: {report-type}
   SUMMARY: {one sentence}
   NEXT_INPUT: {comma-separated report types for next agent}
   ---
   {2-5 bullet key points}
```

## Waiting for Agent Completion

Do NOT use TaskOutput. Instead, use the `wait-for-report.sh` script:

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/wait-for-report.sh {WORKFLOW_DIR}/{name}-report.md
```

This script:
1. Polls every 10 seconds until the report file appears
2. Returns when the file is ready

Note: Stale reports are not an issue because each workflow run uses a unique TASK_ID directory.

For multiple files (parallel agents):
```bash
${CLAUDE_PLUGIN_ROOT}/scripts/wait-for-report.sh {WORKFLOW_DIR}/file1-report.md {WORKFLOW_DIR}/file2-report.md
```

Then read the short report file to get the STATUS and decide next action:
```
Read: {WORKFLOW_DIR}/{name}-report.md
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
mkdir -p {WORKFLOW_DIR}
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

**Step 1: Remove stale signal file (ensures wait-for-report.sh waits for fresh output):**
```bash
${CLAUDE_PLUGIN_ROOT}/scripts/remove-report.sh {WORKFLOW_DIR}/{name}-report.md
```

**Step 2: Launch the agent:**
```
Task tool:
  subagent_type: {agent-name}
  run_in_background: true
  prompt: |
    ## Workflow Context
    TASK_ID: {TASK_ID}
    WORKFLOW_DIR: {WORKFLOW_DIR}

    ## Your Task
    {task description}

    ## Input Reports
    Retrieve from MCP storage (taskId={TASK_ID}):
    {list of reportType values to retrieve, e.g., "requirements", "plan"}

    ## Output
    1. Save FULL report to MCP storage:
       - taskId: {TASK_ID}
       - reportType: {report-type}
       - content: <your full report>

    2. Write SHORT status to file: {WORKFLOW_DIR}/{name}-report.md
       The short report MUST contain ONLY:
       STATUS: {PASS|PARTIAL|FAIL|DONE|ERROR}
       REPORT_TYPE: {report-type}
       SUMMARY: {one sentence}
       NEXT_INPUT: {comma-separated report types for next agent}
       ---
       {2-5 bullet key points}
```

**Step 3: Wait for completion:**
```bash
${CLAUDE_PLUGIN_ROOT}/scripts/wait-for-report.sh {WORKFLOW_DIR}/{name}-report.md
```

**Step 4: Read the short report and parse STATUS to decide next action:**
```
Read: {WORKFLOW_DIR}/{name}-report.md
```

---

## Workflow Steps

### Step 0: Initialize

1. Generate TASK_ID (see "Task ID Generation" above)
2. Set `WORKFLOW_DIR = .workflow/{TASK_ID}`
3. Create `{WORKFLOW_DIR}/` directory
4. Create `metadata.json`

### Step 1: Requirements Analysis (business-analyst)

Remove: `${CLAUDE_PLUGIN_ROOT}/scripts/remove-report.sh {WORKFLOW_DIR}/requirements-report.md`

Launch in foreground:
```
subagent_type: business-analyst
run_in_background: false
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}
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
  1. Save FULL report to MCP storage:
     - taskId: {TASK_ID}
     - reportType: "requirements"
     - content: Include Feature Understanding, Affected Domains, Clarifications, Behavioral Requirements (REQ-1, REQ-2, etc.)
  2. Write SHORT status to file: {WORKFLOW_DIR}/requirements-report.md
```

Wait: `${CLAUDE_PLUGIN_ROOT}/scripts/wait-for-report.sh {WORKFLOW_DIR}/requirements-report.md`
Read: `{WORKFLOW_DIR}/requirements-report.md`

### Step 2: Planning (plan-creator)

Remove: `${CLAUDE_PLUGIN_ROOT}/scripts/remove-report.sh {WORKFLOW_DIR}/plan-report.md`

Launch in background:
```
subagent_type: plan-creator
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}
  WORKFLOW_DIR: {WORKFLOW_DIR}

  ## Task
  Create implementation and testing plan for the feature.

  ## Input Reports
  Retrieve from MCP storage (taskId={TASK_ID}):
  - reportType: "requirements"

  ## Output
  1. Save FULL report to MCP storage:
     - taskId: {TASK_ID}
     - reportType: "plan"
     - content: <your implementation and testing plan>
  2. Write SHORT status to file: {WORKFLOW_DIR}/plan-report.md
```

Wait: `${CLAUDE_PLUGIN_ROOT}/scripts/wait-for-report.sh {WORKFLOW_DIR}/plan-report.md`
Read: `{WORKFLOW_DIR}/plan-report.md`

### Step 3: Test Design - RED Stage (automation-qa)

Remove: `${CLAUDE_PLUGIN_ROOT}/scripts/remove-report.sh {WORKFLOW_DIR}/tests-design-report.md`

Launch in background:
```
subagent_type: automation-qa
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}
  WORKFLOW_DIR: {WORKFLOW_DIR}

  ## Task
  Design and write tests for the planned behavior (RED stage).
  - Normal paths
  - Edge cases
  - Error conditions

  After writing tests, run them to confirm they FAIL (RED).
  Use /run-tests with the narrowest scope.

  ## Input Reports
  Retrieve from MCP storage (taskId={TASK_ID}):
  Required:
  - reportType: "requirements"
  - reportType: "plan"
  Optional (retrieve if workflow iteration - contains feedback requiring new/updated tests):
  - reportType: "tests-review"
  - reportType: "stabilization"
  - reportType: "acceptance"
  - reportType: "code-review"

  ## Output
  1. Save FULL report to MCP storage:
     - taskId: {TASK_ID}
     - reportType: "tests-design"
     - content: <your test design report>
  2. Write SHORT status to file: {WORKFLOW_DIR}/tests-design-report.md
```

Wait: `${CLAUDE_PLUGIN_ROOT}/scripts/wait-for-report.sh {WORKFLOW_DIR}/tests-design-report.md`
Read: `{WORKFLOW_DIR}/tests-design-report.md`

### Step 4: Test Quality Gate (tests-reviewer)

Remove: `${CLAUDE_PLUGIN_ROOT}/scripts/remove-report.sh {WORKFLOW_DIR}/tests-review-report.md`

Launch in background:
```
subagent_type: tests-reviewer
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}
  WORKFLOW_DIR: {WORKFLOW_DIR}

  ## Task
  Review the tests for quality. Apply your loaded skills.
  Return verdict: PASS / PARTIAL / FAIL

  ## Input Reports
  Retrieve from MCP storage (taskId={TASK_ID}):
  - reportType: "requirements"
  - reportType: "plan"
  - reportType: "tests-design"

  ## Output
  1. Save FULL report to MCP storage:
     - taskId: {TASK_ID}
     - reportType: "tests-review"
     - content: <your test review report with verdict>
  2. Write SHORT status to file: {WORKFLOW_DIR}/tests-review-report.md
```

Wait: `${CLAUDE_PLUGIN_ROOT}/scripts/wait-for-report.sh {WORKFLOW_DIR}/tests-review-report.md`
Read: `{WORKFLOW_DIR}/tests-review-report.md`

**⛔ MANDATORY GATE - NO EXCEPTIONS, NO RATIONALIZATION:**

You MUST NOT proceed to Step 5 unless STATUS == PASS.

- Do NOT rationalize skipping this gate ("tests are adequate", "will fix later", etc.)
- Do NOT use your own judgment to override this gate
- PARTIAL means the loop MUST execute - no exceptions

```
LOOP while STATUS != PASS (max 5 iterations):
  IF STATUS is PARTIAL or FAIL:
    1. Execute Step 3 (automation-qa updates tests based on feedback)
    2. Execute Step 4 (tests-reviewer re-reviews)
    3. Read {WORKFLOW_DIR}/tests-review-report.md again
    4. Check STATUS again
  END IF
END LOOP
```

**HARD STOP: Only proceed to Step 5 after STATUS == PASS.**

### Step 5: Implementation - GREEN Stage (backend-developer)

Remove: `${CLAUDE_PLUGIN_ROOT}/scripts/remove-report.sh {WORKFLOW_DIR}/implementation-report.md`

Launch in background:
```
subagent_type: backend-developer
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}
  WORKFLOW_DIR: {WORKFLOW_DIR}

  ## Task
  Implement the feature to make tests pass (GREEN stage).
  - Work in small incremental steps
  - Run /run-tests after each step
  - Continue until all feature tests are GREEN

  ## Input Reports
  Retrieve from MCP storage (taskId={TASK_ID}):
  Required:
  - reportType: "requirements"
  - reportType: "plan"
  - reportType: "tests-design"
  Optional (retrieve if workflow iteration - contains feedback requiring fixes):
  - reportType: "tests-review"
  - reportType: "stabilization"
  - reportType: "acceptance"
  - reportType: "performance"
  - reportType: "security"
  - reportType: "code-review"

  ## Output
  1. Save FULL report to MCP storage:
     - taskId: {TASK_ID}
     - reportType: "implementation"
     - content: <your implementation report>
  2. Write SHORT status to file: {WORKFLOW_DIR}/implementation-report.md
```

Wait: `${CLAUDE_PLUGIN_ROOT}/scripts/wait-for-report.sh {WORKFLOW_DIR}/implementation-report.md`
Read: `{WORKFLOW_DIR}/implementation-report.md`

### Step 6: Stabilization Gate (automation-qa)

Remove: `${CLAUDE_PLUGIN_ROOT}/scripts/remove-report.sh {WORKFLOW_DIR}/stabilization-report.md`

Launch in background:
```
subagent_type: automation-qa
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}
  WORKFLOW_DIR: {WORKFLOW_DIR}

  ## Task
  Run broader test scope and assess stability:
  - Identify regression risks
  - Run package-level or broader /run-tests
  - Report if additional tests are needed

  Return verdict: PASS / PARTIAL / FAIL

  ## Input Reports
  Retrieve from MCP storage (taskId={TASK_ID}):
  - reportType: "requirements"
  - reportType: "plan"
  - reportType: "implementation"

  ## Output
  1. Save FULL report to MCP storage:
     - taskId: {TASK_ID}
     - reportType: "stabilization"
     - content: <your stabilization report with verdict>
  2. Write SHORT status to file: {WORKFLOW_DIR}/stabilization-report.md
```

Wait: `${CLAUDE_PLUGIN_ROOT}/scripts/wait-for-report.sh {WORKFLOW_DIR}/stabilization-report.md`
Read: `{WORKFLOW_DIR}/stabilization-report.md`

**⛔ MANDATORY GATE - NO EXCEPTIONS, NO RATIONALIZATION:**

You MUST NOT proceed to Step 7 unless STATUS == PASS.

- Do NOT rationalize skipping this gate ("will address later", "minor issues", etc.)
- Do NOT use your own judgment to override this gate
- PARTIAL means the loop MUST execute - no exceptions

```
LOOP while STATUS != PASS (max 5 iterations):
  IF STATUS is PARTIAL or FAIL:
    1. Execute Step 3 (automation-qa writes/updates tests for issues - RED)
    2. Execute Step 5 (backend-developer fixes - GREEN)
    3. Execute Step 6 (automation-qa re-runs stabilization check)
    4. Read {WORKFLOW_DIR}/stabilization-report.md again
    5. Check STATUS again
  END IF
END LOOP
```

**HARD STOP: Only proceed to Step 7 after STATUS == PASS.**

### Step 7: Acceptance Review (acceptance-reviewer)

Remove: `${CLAUDE_PLUGIN_ROOT}/scripts/remove-report.sh {WORKFLOW_DIR}/acceptance-report.md`

Launch in background:
```
subagent_type: acceptance-reviewer
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}
  WORKFLOW_DIR: {WORKFLOW_DIR}

  ## Task
  Verify all requirements are met:
  - Check each REQ-N against implementation
  - Identify functional gaps

  Return verdict: PASS / PARTIAL / FAIL

  ## Input Reports
  Retrieve from MCP storage (taskId={TASK_ID}):
  - reportType: "requirements"
  - reportType: "plan"
  - reportType: "implementation"
  - reportType: "stabilization"

  ## Output
  1. Save FULL report to MCP storage:
     - taskId: {TASK_ID}
     - reportType: "acceptance"
     - content: <your acceptance review report with verdict>
  2. Write SHORT status to file: {WORKFLOW_DIR}/acceptance-report.md
```

Wait: `${CLAUDE_PLUGIN_ROOT}/scripts/wait-for-report.sh {WORKFLOW_DIR}/acceptance-report.md`
Read: `{WORKFLOW_DIR}/acceptance-report.md`

**⛔ MANDATORY GATE - NO EXCEPTIONS, NO RATIONALIZATION:**

You MUST NOT proceed to Step 8 unless STATUS == PASS.

- Do NOT rationalize skipping this gate ("requirements mostly met", "minor gaps", etc.)
- Do NOT use your own judgment to override this gate
- PARTIAL means the loop MUST execute - no exceptions

```
LOOP while STATUS != PASS (max 5 iterations):
  IF STATUS is PARTIAL or FAIL:
    1. Execute Step 3 (automation-qa adds tests for gaps - RED)
    2. Execute Step 5 (backend-developer implements - GREEN)
    3. Execute Step 7 (acceptance-reviewer re-checks)
    4. Read {WORKFLOW_DIR}/acceptance-report.md again
    5. Check STATUS again
  END IF
END LOOP
```

**HARD STOP: Only proceed to Step 8 after STATUS == PASS.**

### Step 8: Performance & Security Check (Parallel)

Remove: `${CLAUDE_PLUGIN_ROOT}/scripts/remove-report.sh {WORKFLOW_DIR}/performance-report.md {WORKFLOW_DIR}/security-report.md`

Launch BOTH agents IN PARALLEL (single message, multiple Task tool calls):

**First Task call (performance-specialist):**
```
subagent_type: performance-specialist
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}
  WORKFLOW_DIR: {WORKFLOW_DIR}

  ## Task
  Analyze the implementation for performance issues.
  Apply your loaded skills (`backend-performance`, `algorithm-efficiency`).
  Classify findings as BLOCKING or NON-BLOCKING.
  Return verdict: PASS / PARTIAL / FAIL

  ## Input Reports
  Retrieve from MCP storage (taskId={TASK_ID}):
  - reportType: "implementation"

  ## Output
  1. Save FULL report to MCP storage:
     - taskId: {TASK_ID}
     - reportType: "performance"
     - content: <your performance analysis report with verdict>
  2. Write SHORT status to file: {WORKFLOW_DIR}/performance-report.md
```

**Second Task call (application-security-specialist) - SAME MESSAGE:**
```
subagent_type: application-security-specialist
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}
  WORKFLOW_DIR: {WORKFLOW_DIR}

  ## Task
  Analyze the implementation for security vulnerabilities.
  Apply your loaded skill (`web-api-security`).
  Classify findings as BLOCKING or NON-BLOCKING.
  Return verdict: PASS / PARTIAL / FAIL

  ## Input Reports
  Retrieve from MCP storage (taskId={TASK_ID}):
  - reportType: "implementation"

  ## Output
  1. Save FULL report to MCP storage:
     - taskId: {TASK_ID}
     - reportType: "security"
     - content: <your security analysis report with verdict>
  2. Write SHORT status to file: {WORKFLOW_DIR}/security-report.md
```

Wait: `${CLAUDE_PLUGIN_ROOT}/scripts/wait-for-report.sh {WORKFLOW_DIR}/performance-report.md {WORKFLOW_DIR}/security-report.md`
Read: `{WORKFLOW_DIR}/performance-report.md` and `{WORKFLOW_DIR}/security-report.md`

**⛔ MANDATORY GATE - NO EXCEPTIONS, NO RATIONALIZATION:**

You MUST NOT proceed to Step 9 unless BOTH STATUS == PASS (or only NON-BLOCKING issues remain).

- Do NOT rationalize skipping this gate ("performance is acceptable", "security is minor", etc.)
- Do NOT use your own judgment to override this gate
- BLOCKING issues mean the loop MUST execute - no exceptions

```
LOOP while EITHER STATUS has BLOCKING issues (max 5 iterations):
  IF performance-report or security-report has STATUS PARTIAL/FAIL with BLOCKING issues:
    1. Execute Step 5 (backend-developer fixes BLOCKING issues from both reviews)
    2. Execute Step 8 (re-run both performance and security checks)
    3. Read {WORKFLOW_DIR}/performance-report.md and {WORKFLOW_DIR}/security-report.md again
    4. Check both STATUS values again
  END IF
END LOOP
```

**HARD STOP: Only proceed to Step 9 after BOTH STATUS == PASS (or only NON-BLOCKING remain).**

### Step 9: Refactoring (refactorer)

Remove: `${CLAUDE_PLUGIN_ROOT}/scripts/remove-report.sh {WORKFLOW_DIR}/refactoring-report.md`

Launch in background:
```
subagent_type: refactorer
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}
  WORKFLOW_DIR: {WORKFLOW_DIR}

  ## Task
  Perform behavior-preserving cleanup.
  Apply your loaded skills (`refactoring-patterns`, `design-assessment`, `design-patterns`).
  Run /run-tests after each refactor step.
  Record larger refactors as follow-up tasks, don't do them now.

  ## Input Reports
  Retrieve from MCP storage (taskId={TASK_ID}):
  Required:
  - reportType: "implementation"
  Optional (retrieve if workflow iteration - contains structural issues to address):
  - reportType: "code-review"

  ## Output
  1. Save FULL report to MCP storage:
     - taskId: {TASK_ID}
     - reportType: "refactoring"
     - content: <your refactoring report>
  2. Write SHORT status to file: {WORKFLOW_DIR}/refactoring-report.md
```

Wait: `${CLAUDE_PLUGIN_ROOT}/scripts/wait-for-report.sh {WORKFLOW_DIR}/refactoring-report.md`
Read: `{WORKFLOW_DIR}/refactoring-report.md`

### Step 10: Code Review (code-reviewer)

Remove: `${CLAUDE_PLUGIN_ROOT}/scripts/remove-report.sh {WORKFLOW_DIR}/code-review-report.md`

Launch in background:
```
subagent_type: code-reviewer
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}
  WORKFLOW_DIR: {WORKFLOW_DIR}

  ## Task
  Review the code for quality issues.
  Apply your loaded skills (`code-review-checklist`, `design-assessment`).
  Classify findings as BLOCKING or NON-BLOCKING.
  For each BLOCKING issue, specify route:
  - "ROUTE: functional" → needs tests + implementation fix
  - "ROUTE: structural" → needs refactoring

  Return verdict: PASS / PARTIAL / FAIL

  ## Input Reports
  Retrieve from MCP storage (taskId={TASK_ID}):
  - reportType: "implementation"
  - reportType: "refactoring"

  ## Output
  1. Save FULL report to MCP storage:
     - taskId: {TASK_ID}
     - reportType: "code-review"
     - content: <your code review report with verdict>
  2. Write SHORT status to file: {WORKFLOW_DIR}/code-review-report.md
```

Wait: `${CLAUDE_PLUGIN_ROOT}/scripts/wait-for-report.sh {WORKFLOW_DIR}/code-review-report.md`
Read: `{WORKFLOW_DIR}/code-review-report.md`

**⛔ MANDATORY GATE - NO EXCEPTIONS, NO RATIONALIZATION:**

You MUST NOT proceed to Step 11 unless STATUS == PASS (or only NON-BLOCKING issues remain).

- Do NOT rationalize skipping this gate ("code is good enough", "issues are minor", etc.)
- Do NOT use your own judgment to override this gate
- BLOCKING issues mean the loop MUST execute - no exceptions

```
LOOP while STATUS has BLOCKING issues (max 5 iterations):
  IF STATUS is PARTIAL or FAIL with BLOCKING issues:
    1. Retrieve code-review report from MCP storage to parse BLOCKING issues by route
    2. FOR EACH functional issue (ROUTE: functional):
       - Execute Step 3 (automation-qa adds/updates tests - RED)
       - Execute Step 5 (backend-developer fixes - GREEN)
    3. FOR EACH structural issue (ROUTE: structural):
       - Execute Step 9 (refactorer addresses structural issues)
    4. Execute Step 10 (code-reviewer re-reviews)
    5. Read {WORKFLOW_DIR}/code-review-report.md again
    6. Check STATUS again
  END IF
END LOOP
```

**HARD STOP: Only proceed to Step 11 after STATUS == PASS (or only NON-BLOCKING remain).**

### Step 11: Documentation (documentation-updater)

Remove: `${CLAUDE_PLUGIN_ROOT}/scripts/remove-report.sh {WORKFLOW_DIR}/documentation-report.md`

Launch in background:
```
subagent_type: documentation-updater
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}
  WORKFLOW_DIR: {WORKFLOW_DIR}

  ## Task
  Update documentation impacted by the change:
  - README usage examples
  - Configuration/env var references
  - Architecture notes
  - Runbooks

  Keep changes minimal and tied to implemented behavior.

  ## Input Reports
  Retrieve from MCP storage (taskId={TASK_ID}):
  - reportType: "requirements"
  - reportType: "plan"
  - reportType: "implementation"

  ## Output
  1. Save FULL report to MCP storage:
     - taskId: {TASK_ID}
     - reportType: "documentation"
     - content: <your documentation update report>
  2. Write SHORT status to file: {WORKFLOW_DIR}/documentation-report.md
```

Wait: `${CLAUDE_PLUGIN_ROOT}/scripts/wait-for-report.sh {WORKFLOW_DIR}/documentation-report.md`
Read: `{WORKFLOW_DIR}/documentation-report.md`

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

The workflow-completion hook will generate the final summary by:
- Reading signal files from `{WORKFLOW_DIR}/`
- Retrieving full reports from MCP storage using the TASK_ID

---

## Non-Negotiable Constraints

1. **TDD is mandatory:**
   - Tests before implementation
   - Tests reviewed (PASS) before implementation begins
   - /run-tests after every implementation or refactor step

2. **Background agents with file-based signaling:**
   - All agents MUST run with `run_in_background: true`
   - Do NOT use TaskOutput - use scripts instead
   - **Before launching agent:** `${CLAUDE_PLUGIN_ROOT}/scripts/remove-report.sh {WORKFLOW_DIR}/{name}-report.md`
   - **After launching agent:** `${CLAUDE_PLUGIN_ROOT}/scripts/wait-for-report.sh {WORKFLOW_DIR}/{name}-report.md`
   - The wait script polls until the signal file appears
   - Then read the signal file to get STATUS

3. **MCP-based full reports, file-based signals:**
   - Agents save FULL reports to MCP storage with taskId and reportType
   - Agents write SHORT status to file: `{WORKFLOW_DIR}/{name}-report.md`
   - Orchestrator only reads the short `-report.md` signal files
   - Next agent retrieves previous reports from MCP storage

4. **No scope creep:**
   - Do not introduce features beyond $ARGUMENTS

5. **Context in every prompt:**
   - Every agent prompt MUST include `TASK_ID: {TASK_ID}` and `WORKFLOW_DIR: {WORKFLOW_DIR}`

6. **Verify MCP report saved:**
   - After agent completes (signal file appears), verify the MCP save-report call succeeded
   - If MCP save failed: HALT and report error to user

7. **Handle STATUS: ERROR:**
   - If any agent's `-report.md` contains `STATUS: ERROR`, HALT the workflow immediately
   - Do NOT proceed to the next step
   - Do NOT retry the failed agent
   - Report to user with details from the error response

8. **Missing input report protocol:**
   - If an agent cannot retrieve a required report via MCP:
     1. Agent logs which reportType was not found
     2. If optional: proceed without it
     3. If required: write `STATUS: ERROR` to its `-report.md` with details
   - Orchestrator halts and reports to user

9. **Save failure protocol:**
   - If an agent cannot save its report via MCP:
     1. Agent retries once
     2. If still fails: write `STATUS: ERROR` to its `-report.md` with error details
     3. NEVER write DONE/PASS to `-report.md` if MCP save-report failed
   - Orchestrator halts and reports to user with recovery steps

10. **Task isolation:**
    - Each workflow MUST use its own unique TASK_ID
    - Signal files go in `{WORKFLOW_DIR}/` subdirectory
    - MCP reports are keyed by TASK_ID + reportType
    - This allows multiple workflows to run concurrently
