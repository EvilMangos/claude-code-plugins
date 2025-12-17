---
description: Develops a backend feature end-to-end using strict TDD with planning, test design, test review gate, implementation, QA, acceptance review, performance check, security check, refactoring, code review, and documentation updates.
argument-hint: [ feature-description ]
allowed-tools: Read, Edit, Write, Grep, Glob, Task, SlashCommand, Bash
---

# Feature Development Workflow (Background Agent Orchestration)

You are orchestrating a multistep **TDD** feature workflow for this repository.

The user request is:

> $ARGUMENTS

## Architecture: Background Agents with File-Based Context

This workflow uses background agents to minimize context window usage:

1. **Each agent runs in background** (`run_in_background: true`)
2. **Each agent writes full report to file** (`.workflow/{step}-{name}.md`)
3. **Each agent returns brief status** (STATUS, FILE, SUMMARY, NEXT_INPUT)
4. **Orchestrator only sees status** - full context stays in files
5. **Next agent reads previous files** - gets context from disk

**Critical: Always include these instructions in every agent prompt:**
```
You MUST use the workflow-report-format skill for output formatting.
Write your FULL report to: .workflow/{step}-{name}.md
Return ONLY the brief orchestrator response (max 10 lines) as your final output.
```

## Workflow State Directory

Before starting, initialize the workflow directory:

```bash
mkdir -p .workflow/loop-iterations
```

Create `.workflow/metadata.json`:
```json
{
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

    ## Your Task
    {task description}

    ## Input Files to Read
    {list of .workflow/*.md files to read}

    ## Output
    1. Write FULL report to: .workflow/{step}-{name}.md
    2. Return ONLY this format:
       STATUS: {PASS|PARTIAL|FAIL|DONE}
       FILE: .workflow/{step}-{name}.md
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

1. Create `.workflow/` directory
2. Create `metadata.json`
3. Restate the feature in your own words
4. Identify affected domains/packages
5. List assumptions if anything is ambiguous
6. Derive behavioral requirements (REQ-1, REQ-2, etc.)

Write requirements to `.workflow/00-requirements.md`:
```markdown
# Feature Requirements

**Feature:** $ARGUMENTS

## Assumptions
- {assumption}

## Requirements
1. REQ-1: {requirement}
2. REQ-2: {requirement}
```

### Step 1: Planning (plan-creator)

Launch in background:
```
subagent_type: plan-creator
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Task
  Create implementation and testing plan for the feature.

  ## Input
  Read: .workflow/00-requirements.md

  ## Output
  1. Write FULL report to: .workflow/01-plan.md
  2. Return brief status only
```

Wait with `TaskOutput(block: true)`.

### Step 2: Test Design - RED Stage (automation-qa)

Launch in background:
```
subagent_type: automation-qa
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Task
  Design and write tests for the planned behavior (RED stage).
  - Normal paths
  - Edge cases
  - Error conditions

  After writing tests, run them to confirm they FAIL (RED).
  Use /run-tests with the narrowest scope.

  ## Input
  Read: .workflow/00-requirements.md, .workflow/01-plan.md

  ## Output
  1. Write FULL report to: .workflow/02-tests-design.md
  2. Return brief status only
```

Wait with `TaskOutput(block: true)`.

### Step 3: Test Quality Gate (tests-reviewer)

Launch in background:
```
subagent_type: tests-reviewer
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Task
  Review the tests for quality. Apply your loaded skills.
  Return verdict: PASS / PARTIAL / FAIL

  ## Input
  Read: .workflow/00-requirements.md, .workflow/01-plan.md, .workflow/02-tests-design.md

  ## Output
  1. Write FULL report to: .workflow/03-tests-review.md
  2. Return brief status only
```

Wait with `TaskOutput(block: true)`.

**Loop Logic:**
- If STATUS is PARTIAL or FAIL:
  1. Launch automation-qa to fix tests (reads .workflow/03-tests-review.md)
  2. Re-run tests-reviewer
  3. Repeat until PASS
- Do NOT proceed to implementation until PASS

### Step 4: Implementation - GREEN Stage (backend-developer)

Launch in background:
```
subagent_type: backend-developer
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Task
  Implement the feature to make tests pass (GREEN stage).
  - Work in small incremental steps
  - Run /run-tests after each step
  - Continue until all feature tests are GREEN

  ## Input
  Read: .workflow/00-requirements.md, .workflow/01-plan.md, .workflow/02-tests-design.md

  ## Output
  1. Write FULL report to: .workflow/04-implementation.md
  2. Return brief status only
```

Wait with `TaskOutput(block: true)`.

### Step 5: Stabilization Gate (automation-qa)

Launch in background:
```
subagent_type: automation-qa
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Task
  Run broader test scope and assess stability:
  - Identify regression risks
  - Run package-level or broader /run-tests
  - Report if additional tests are needed

  Return verdict: PASS / PARTIAL / FAIL

  ## Input
  Read: .workflow/00-requirements.md, .workflow/01-plan.md, .workflow/04-implementation.md

  ## Output
  1. Write FULL report to: .workflow/05-stabilization.md
  2. Return brief status only
```

Wait with `TaskOutput(block: true)`.

**Loop Logic (TDD):**
- If STATUS is PARTIAL or FAIL:
  1. automation-qa writes/updates tests (RED)
  2. backend-developer fixes (GREEN)
  3. Re-run stabilization
  4. Repeat until PASS

### Step 6: Acceptance Review (acceptance-reviewer)

Launch in background:
```
subagent_type: acceptance-reviewer
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Task
  Verify all requirements are met:
  - Check each REQ-N against implementation
  - Identify functional gaps

  Return verdict: PASS / PARTIAL / FAIL

  ## Input
  Read: .workflow/00-requirements.md, .workflow/01-plan.md, .workflow/04-implementation.md, .workflow/05-stabilization.md

  ## Output
  1. Write FULL report to: .workflow/06-acceptance.md
  2. Return brief status only
```

Wait with `TaskOutput(block: true)`.

**Loop Logic (TDD):**
- If STATUS is PARTIAL or FAIL:
  1. automation-qa adds tests for gaps (RED)
  2. backend-developer implements (GREEN)
  3. Re-run acceptance
  4. Repeat until PASS

### Step 7: Performance Check Loop (performance-specialist ↔ backend-developer)

Initialize loop state: `iteration = 1`

**Loop Start:**

**If iteration == 1:** Launch initial review:
```
subagent_type: performance-specialist
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Task
  Analyze the implementation for performance issues.
  Apply your loaded skills (`backend-performance`, `algorithm-efficiency`).
  Classify findings as BLOCKING or NON-BLOCKING.
  Return verdict: PASS / PARTIAL / FAIL

  ## Iteration
  This is review iteration 1 (initial review).

  ## Input
  Read: .workflow/04-implementation.md

  ## Output
  1. Write FULL report to: .workflow/07-performance.md
  2. Return brief status only
```

**If iteration > 1:** Launch re-review:
```
subagent_type: performance-specialist
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Task
  Re-review performance after fixes were applied.
  Check if BLOCKING issues from previous review are resolved.

  ## Iteration
  This is review iteration {iteration}.

  ## Input
  Read:
  - .workflow/07-performance.md (original findings)
  - .workflow/loop-iterations/07-performance-fix-{iteration-1}.md (latest fix)
  - .workflow/04-implementation.md (current implementation)

  ## Output
  1. Write FULL report to: .workflow/loop-iterations/07-performance-review-{iteration}.md
  2. Return brief status only
```

Wait with `TaskOutput(block: true)`.

**If STATUS is FAIL or PARTIAL with BLOCKING issues:**

Launch fixer:
```
subagent_type: backend-developer
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Task
  Fix the BLOCKING performance issues identified in the review.
  Run /run-tests after each fix to ensure behavior is preserved.

  ## Iteration
  This is fix iteration {iteration}.

  ## Input
  Read: {latest review file - either .workflow/07-performance.md or .workflow/loop-iterations/07-performance-review-{iteration}.md}

  ## Focus On
  Address ONLY the BLOCKING issues. NON-BLOCKING issues are deferred.

  ## Output
  1. Write FULL report to: .workflow/loop-iterations/07-performance-fix-{iteration}.md
  2. Return brief status only
```

Wait with `TaskOutput(block: true)`.
Increment `iteration`.
**Go back to Loop Start.**

**Loop Exit:** STATUS is PASS, or only NON-BLOCKING remain, or iteration > 5 (max)

### Step 8: Security Check Loop (application-security-specialist ↔ backend-developer)

Initialize loop state: `iteration = 1`

**Loop Start:**

**If iteration == 1:** Launch initial review:
```
subagent_type: application-security-specialist
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Task
  Analyze the implementation for security vulnerabilities.
  Apply your loaded skill (`web-api-security`).
  Classify findings as BLOCKING or NON-BLOCKING.
  Return verdict: PASS / PARTIAL / FAIL

  ## Iteration
  This is review iteration 1 (initial review).

  ## Input
  Read: .workflow/04-implementation.md

  ## Output
  1. Write FULL report to: .workflow/08-security.md
  2. Return brief status only
```

**If iteration > 1:** Launch re-review:
```
subagent_type: application-security-specialist
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Task
  Re-review security after fixes were applied.
  Check if BLOCKING vulnerabilities from previous review are resolved.

  ## Iteration
  This is review iteration {iteration}.

  ## Input
  Read:
  - .workflow/08-security.md (original findings)
  - .workflow/loop-iterations/08-security-fix-{iteration-1}.md (latest fix)
  - .workflow/04-implementation.md (current implementation)

  ## Output
  1. Write FULL report to: .workflow/loop-iterations/08-security-review-{iteration}.md
  2. Return brief status only
```

Wait with `TaskOutput(block: true)`.

**If STATUS is FAIL or PARTIAL with BLOCKING issues:**

Launch fixer:
```
subagent_type: backend-developer
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Task
  Fix the BLOCKING security vulnerabilities identified in the review.
  Run /run-tests after each fix to ensure behavior is preserved.

  ## Iteration
  This is fix iteration {iteration}.

  ## Input
  Read: {latest review file - either .workflow/08-security.md or .workflow/loop-iterations/08-security-review-{iteration}.md}

  ## Focus On
  Address ONLY the BLOCKING vulnerabilities. NON-BLOCKING hardening is deferred.

  ## Output
  1. Write FULL report to: .workflow/loop-iterations/08-security-fix-{iteration}.md
  2. Return brief status only
```

Wait with `TaskOutput(block: true)`.
Increment `iteration`.
**Go back to Loop Start.**

**Loop Exit:** STATUS is PASS, or only NON-BLOCKING remain, or iteration > 5 (max)

### Step 9: Refactoring (refactorer)

Launch in background:
```
subagent_type: refactorer
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Task
  Perform behavior-preserving cleanup.
  Apply your loaded skills (`refactoring-patterns`, `design-assessment`, `design-patterns`).
  Run /run-tests after each refactor step.
  Record larger refactors as follow-up tasks, don't do them now.

  ## Input
  Read: .workflow/04-implementation.md

  ## Output
  1. Write FULL report to: .workflow/09-refactoring.md
  2. Return brief status only
```

Wait with `TaskOutput(block: true)`.

### Step 10: Code Review Loop (code-reviewer)

Initialize loop state: `iteration = 1`

**Loop Start:**

**If iteration == 1:** Launch initial review:
```
subagent_type: code-reviewer
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Task
  Review the code for quality issues.
  Apply your loaded skills (`code-review-checklist`, `design-assessment`).
  Classify findings as BLOCKING or NON-BLOCKING.
  For each BLOCKING issue, specify route:
  - "ROUTE: functional" → needs automation-qa (tests) + backend-developer (fix)
  - "ROUTE: structural" → needs refactorer

  Return verdict: PASS / PARTIAL / FAIL

  ## Iteration
  This is review iteration 1 (initial review).

  ## Input
  Read: .workflow/04-implementation.md, .workflow/09-refactoring.md

  ## Output
  1. Write FULL report to: .workflow/10-code-review.md
  2. Return brief status only
```

**If iteration > 1:** Launch re-review:
```
subagent_type: code-reviewer
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Task
  Re-review code quality after fixes were applied.
  Check if BLOCKING issues from previous review are resolved.

  ## Iteration
  This is review iteration {iteration}.

  ## Input
  Read:
  - .workflow/10-code-review.md (original findings)
  - .workflow/loop-iterations/10-code-review-fix-{iteration-1}.md (latest fix)
  - .workflow/04-implementation.md, .workflow/09-refactoring.md (current state)

  ## Output
  1. Write FULL report to: .workflow/loop-iterations/10-code-review-review-{iteration}.md
  2. Return brief status only
```

Wait with `TaskOutput(block: true)`.

**If STATUS is FAIL or PARTIAL with BLOCKING issues:**

Parse BLOCKING issues by route from review file:
- Functional issues (ROUTE: functional) → TDD loop
- Structural issues (ROUTE: structural) → refactorer

**For functional issues:**
1. Launch automation-qa to add/update tests (RED)
2. Launch backend-developer to fix (GREEN)
3. Write combined fix report to `.workflow/loop-iterations/10-code-review-fix-{iteration}.md`

**For structural issues:**
```
subagent_type: refactorer
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Task
  Fix the BLOCKING structural/design issues identified in code review.
  Run /run-tests after each refactor step.

  ## Iteration
  This is fix iteration {iteration}.

  ## Input
  Read: {latest review file}

  ## Focus On
  Address ONLY the BLOCKING structural issues marked "ROUTE: structural".

  ## Output
  1. Write FULL report to: .workflow/loop-iterations/10-code-review-fix-{iteration}.md
  2. Return brief status only
```

Wait with `TaskOutput(block: true)`.
Increment `iteration`.
**Go back to Loop Start.**

**Loop Exit:** STATUS is PASS, or only NON-BLOCKING remain, or iteration > 5 (max), or user accepts trade-offs

### Step 11: Documentation (documentation-updater)

Launch in background:
```
subagent_type: documentation-updater
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Task
  Update documentation impacted by the change:
  - README usage examples
  - Configuration/env var references
  - Architecture notes
  - Runbooks

  Keep changes minimal and tied to implemented behavior.

  ## Input
  Read: .workflow/00-requirements.md, .workflow/01-plan.md, .workflow/04-implementation.md

  ## Output
  1. Write FULL report to: .workflow/11-documentation.md
  2. Return brief status only
```

Wait with `TaskOutput(block: true)`.

### Step 12: Finalize

Update `.workflow/metadata.json`:
```json
{
  "status": "completed",
  "completedAt": "{ISO timestamp}"
}
```

The workflow-completion hook will generate the final summary by reading `.workflow/` files.

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
   - Agents write full reports to files
   - Agents return only brief status to orchestrator
   - Next agent reads previous agent's files

4. **No scope creep:**
   - Do not introduce features beyond $ARGUMENTS

5. **Skill usage:**
   - Every agent prompt MUST mention `workflow-report-format` skill

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
     1. Agent lists `.workflow/` directory contents
     2. Agent attempts to identify alternative file (name variations)
     3. If found: use it and log warning in Handoff Notes
     4. If not found: return `STATUS: ERROR` with file listing
   - Orchestrator halts and reports to user

9. **Write failure protocol:**
   - If an agent cannot write its output file:
     1. Agent attempts recovery (mkdir -p .workflow/loop-iterations)
     2. If still fails: return `STATUS: ERROR` with error details
     3. NEVER return DONE/PASS if file was not written
   - Orchestrator halts and reports to user with recovery steps
