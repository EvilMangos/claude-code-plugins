---
description: Fix a bug using a structured workflow with reproduction, root cause analysis, TDD, implementation, and code review.
argument-hint: <bug-description>
allowed-tools: Read, Edit, Write, Grep, Glob, Task, SlashCommand
---

You are orchestrating a multistep **bug-fixing** workflow for this repository.

The bug report is:

> $ARGUMENTS

You MUST follow this workflow strictly and delegate to the named subagents at each step.
Do not do a subagent's work in the main agent.

Required subagents:

- plan-creator
- automation-qa
- tests-reviewer
- backend-developer
- acceptance-reviewer
- refactorer
- code-reviewer

## Testing

Use `/run-tests <path-or-pattern>` to run tests throughout this workflow.

## Workflow

### 1) Clarify & High-level understanding (main agent)

- Restate the bug in your own words.
- Identify the expected behavior vs actual behavior.
- Identify affected domains/packages/components.
- If anything is ambiguous, ask clarifying questions before proceeding.
- List assumptions explicitly.

### 2) Verify bug / Attempt to reproduce (main agent)

- Attempt to reproduce the bug:
    - If there are existing tests that should catch this bug, run them with `/run-tests`.
    - If no tests exist, try to trigger the bug manually (check logs, trace code paths).
- Document reproduction steps and evidence.
- If the bug cannot be reproduced:
    - Ask the user for more details (environment, exact steps, logs).
    - Do not proceed until the bug is confirmed or a reasonable hypothesis exists.

### 3) Identify bug / Root cause analysis (main agent)

- Explore the codebase to locate the root cause:
    - Trace the code path from the symptom to the source.
    - Check recent changes if relevant (git log, git blame).
    - Identify the specific file(s), function(s), and line(s) causing the issue.
- Document:
    - Root cause explanation.
    - Why the bug occurs (missing check, wrong logic, race condition, etc.).
    - Confidence level (certain, likely, hypothesis).

### 4) Fix planning (delegate to `plan-creator`)

- Invoke `plan-creator` with:
    - The bug description and root cause analysis.
    - The affected files and functions.
- The `plan-creator` should produce:
    - A step-by-step fix plan.
    - Risk assessment (could this fix break other things?).
    - Files to modify and how.
- Adopt or refine the plan before proceeding.

### 5) TDD — Test design & RED stage (delegate to `automation-qa`)

- Before changing any implementation, invoke `automation-qa` with:
    - The bug description and root cause analysis.
    - The affected files and functions.
- The `automation-qa` agent will:
    - Evaluate whether a regression test is warranted for this bug (using its `test-best-practices` skill).
    - If a test is warranted: design and write a test that reproduces the bug.
    - If no test is warranted (trivial fix, no behavioral change worth testing): document why and proceed without a test.
- If a test was created:
    - The test should **fail** with the current buggy code (RED).
    - Run `/run-tests` to confirm the test **fails** (RED).
    - If the test passes unexpectedly:
        - The bug may not be where you think. Re-analyze root cause.
        - Or strengthen the test to properly catch the bug.

### 6) Test quality review gate (conditional, delegate to `tests-reviewer`)

**SKIP if `automation-qa` determined no test was warranted in Step 5.**

- Invoke `tests-reviewer` to review:
    - Does the test actually catch the reported bug?
    - Is the test assertion specific enough?
    - Will the test remain valuable after the fix (regression prevention)?
- Verdict: **PASS / PARTIAL / FAIL**
- If PARTIAL or FAIL:
    - Loop with `automation-qa` to improve the test.
    - Re-run RED verification.
    - Re-run `tests-reviewer`.
- Do not proceed until verdict is PASS.

### 7) Apply fix / GREEN stage (delegate to `backend-developer`)

- Pass to `backend-developer`:
    - The fix plan from `plan-creator`.
    - The root cause analysis.
    - The failing test (if created) and its `/run-tests` invocation.
- The `backend-developer` must:
    - Implement the fix in small, incremental steps.
    - After each step, specify the smallest relevant `/run-tests` invocation.
- You MUST run `/run-tests` after each step.
- If the bug-catching test was created, it should now **pass** (GREEN).
- If tests fail unexpectedly:
    - Analyze and fix, or loop with `automation-qa` if tests need adjustment.

### 8) Broader testing & stabilization (delegate to `automation-qa`)

- Re-invoke `automation-qa` to:
    - Determine if additional regression tests are needed.
    - Provide a broader `/run-tests` invocation (package-level or module-level).
    - Return a stabilization verdict: **PASS / PARTIAL / FAIL**
- You MUST run the broader `/run-tests` invocation.
- If verdict is PARTIAL or FAIL:
    - Loop using TDD:
        - `automation-qa` creates/updates tests (RED).
        - `backend-developer` fixes (GREEN).
    - Re-run broader tests.
    - Re-run `automation-qa` for new verdict.

### 9) Acceptance test (delegate to `acceptance-reviewer`)

- Provide `acceptance-reviewer`:
    - Original bug report (`$ARGUMENTS`).
    - Root cause analysis.
    - Summary of fix and tests.
    - Evidence from Step 8 (test results, stabilization verdict).
- The `acceptance-reviewer` should:
    - Verify the original bug is fixed.
    - Check no new issues were introduced.
    - Produce verdict: **PASS / PARTIAL / FAIL**
- If there are gaps:
    - Loop back using TDD as needed.
    - Re-run acceptance review.

### 10) Quick code review (delegate to `code-reviewer`)

- Invoke `code-reviewer` to evaluate:
    - Fix quality (is this the right solution?).
    - Adherence to project conventions.
    - No unnecessary changes beyond the fix.
    - Test quality (if tests were added).
- Findings classified as:
    - **BLOCKING** (must fix)
    - **NON-BLOCKING** (nice-to-have)
- For BLOCKING issues, apply a reflection loop:
    - Functional issue: `automation-qa` (tests) + `backend-developer` (fix).
    - Structural/style issue: `refactorer` (cleanup) + run `/run-tests`.
- Re-invoke `code-reviewer` after fixes.
- Repeat until no blocking issues remain.

### 11) Refactoring (conditional, delegate to `refactorer`)

**ONLY if Step 10 identified structural issues or the fix introduced code smells.**

- Invoke `refactorer` for behavior-preserving cleanup:
    - Improve structure, naming, clarity.
    - Keep external behavior identical.
- After each refactor step:
    - Run `/run-tests`.
    - If tests fail, fix or revert.
- Do not expand scope beyond what's needed for the bug fix.

## Non-negotiable constraints

- Reproduce or verify the bug before attempting to fix it.
- Always invoke `automation-qa` to evaluate whether a regression test is needed (let the agent decide based on its `test-best-practices` skill).
- After every implementation or refactor step, run the smallest relevant `/run-tests`.
- Do not introduce changes beyond what's needed to fix the reported bug.
- Prefer narrow `/run-tests` invocations unless broader runs are required by the workflow.
