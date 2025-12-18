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
  Review test quality:
  - Requirements → tests mapping completeness
  - Correctness of assertions
  - Assertion strength (would fail for realistic bugs?)
  - Determinism & flake risk

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

**Loop Start:**

Launch in background:
```
subagent_type: performance-specialist
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Task
  Analyze for performance issues:
  - Algorithmic complexity
  - Database query efficiency (N+1, indexes)
  - Memory allocation patterns
  - I/O bottlenecks
  - Caching opportunities

  Classify findings as BLOCKING or NON-BLOCKING.
  Return verdict: PASS / PARTIAL / FAIL

  ## Input
  Read: .workflow/04-implementation.md

  ## Output
  1. Write FULL report to: .workflow/07-performance.md (or loop-iterations/07-performance-{N}.md)
  2. Return brief status only
```

Wait with `TaskOutput(block: true)`.

**If BLOCKING issues:**
1. Launch backend-developer with .workflow/07-performance.md
2. Developer fixes issues, runs /run-tests
3. **Go back to Loop Start** - re-run performance-specialist

**Loop Exit:** STATUS is PASS or only NON-BLOCKING remain

### Step 8: Security Check Loop (application-security-specialist ↔ backend-developer)

**Loop Start:**

Launch in background:
```
subagent_type: application-security-specialist
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Task
  Analyze for security vulnerabilities:
  - Input validation
  - Authentication/authorization
  - Injection vulnerabilities
  - Sensitive data handling
  - OWASP Top 10

  Classify findings as BLOCKING or NON-BLOCKING.
  Return verdict: PASS / PARTIAL / FAIL

  ## Input
  Read: .workflow/04-implementation.md

  ## Output
  1. Write FULL report to: .workflow/08-security.md (or loop-iterations/08-security-{N}.md)
  2. Return brief status only
```

Wait with `TaskOutput(block: true)`.

**If BLOCKING issues:**
1. Launch backend-developer with .workflow/08-security.md
2. Developer fixes vulnerabilities, runs /run-tests
3. **Go back to Loop Start** - re-run security-specialist

**Loop Exit:** STATUS is PASS or only NON-BLOCKING remain

### Step 9: Refactoring (refactorer)

Launch in background:
```
subagent_type: refactorer
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Task
  Behavior-preserving cleanup:
  - Improve structure, naming, separation of concerns
  - Remove duplication
  - Run /run-tests after each refactor step

  Record larger refactors as follow-up tasks, don't do them now.

  ## Input
  Read: .workflow/04-implementation.md

  ## Output
  1. Write FULL report to: .workflow/09-refactoring.md
  2. Return brief status only
```

Wait with `TaskOutput(block: true)`.

### Step 10: Code Review Loop (code-reviewer)

**Loop Start:**

Launch in background:
```
subagent_type: code-reviewer
run_in_background: true
prompt: |
  Use the workflow-report-format skill.

  ## Task
  Review code quality:
  - Architecture alignment
  - Maintainability
  - Style
  - Test design quality

  Classify findings as BLOCKING or NON-BLOCKING.
  For BLOCKING, specify route: automation-qa+backend-developer OR refactorer

  Return verdict: PASS / PARTIAL / FAIL

  ## Input
  Read: .workflow/04-implementation.md, .workflow/09-refactoring.md

  ## Output
  1. Write FULL report to: .workflow/10-code-review.md (or loop-iterations/10-code-review-{N}.md)
  2. Return brief status only
```

Wait with `TaskOutput(block: true)`.

**If BLOCKING issues:**
- Functional issues → automation-qa (tests, RED) + backend-developer (fix, GREEN)
- Structural issues → refactorer (small refactor, run tests)
- **Go back to Loop Start** - re-run code-reviewer

**Loop Exit:** STATUS is PASS or only NON-BLOCKING remain (or user accepts trade-offs)

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
