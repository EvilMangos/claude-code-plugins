---
description: Develop a backend feature end-to-end using strict TDD with planning, test design, test review gate, implementation, QA, acceptance review, refactoring, code review, and documentation updates.
argument-hint: [ feature-description ]
allowed-tools: Read, Grep, Glob, Task, SlashCommand
---

You are orchestrating a multistep **TDD** feature workflow for this repository.

The user request is:

> $ARGUMENTS

You MUST follow this workflow strictly and delegate to the named subagents at each step.
Do not do a subagent's work in the main agent.

Required subagents:

- plan-creator
- automation-qa
- tests-reviewer
- feature-developer
- acceptance-reviewer
- refactorer
- code-reviewer
- documentation-updater

## Testing

Use `/run-tests <path-or-pattern>` to run tests throughout this workflow. The SessionStart hook verifies this command exists.

## Workflow

### 1) Clarify & high-level understanding (main agent)

- Restate the feature in your own words.
- Identify affected domains/packages.
- If anything is ambiguous, list assumptions explicitly.
- Derive a list of **behavioral requirements** (inputs, outputs, edge cases, errors).

### 2) Planning (delegate to `plan-creator`)

- Invoke `plan-creator` to:
    - Explore the relevant code.
    - Produce a step-by-step implementation and testing plan.
    - Map each requirement to concrete code areas and test locations.
    - Highlight risks and open questions.
- Adopt or lightly refine the plan.
- Ensure the plan clearly separates:
    - **Test steps** (what tests to write/update, where).
    - **Implementation steps** (what logic to add/change, where).

### 3) TDD — Test design & RED stage (delegate to `automation-qa`)

- Before changing any implementation, invoke `automation-qa` to:
    - Design and write/update tests for the planned behavior:
        - Normal paths
        - Edge cases
        - Error conditions
    - Place tests in the appropriate test files and fixtures.
    - Provide **exact `/run-tests` invocations** to run just these tests (smallest scope).
- After tests are created/updated:
    - Run the suggested `/run-tests` commands against the current implementation to confirm they **fail** (RED).
- If tests pass unexpectedly:
    - Loop with `automation-qa` to strengthen expectations and/or adjust scenarios.
    - Re-run the RED `/run-tests` commands.

### 4) Test quality review gate (delegate to `tests-reviewer`)

- Immediately after the RED stage, invoke `tests-reviewer` to review:
    - Requirements → tests mapping completeness
    - Correctness: tests verify the right observable behavior
    - Strength: assertions would fail for realistic bugs
    - Determinism & flake risk
- The `tests-reviewer` must return a verdict: **PASS / PARTIAL / FAIL**.
- If verdict is PARTIAL or FAIL:
    - Loop back to `automation-qa` to tighten/fix tests
    - Re-run the RED `/run-tests` commands
    - Re-run `tests-reviewer`
- Do not proceed to implementation until verdict is PASS.

### 5) TDD — Implementation & GREEN stage (delegate to `feature-developer`)

- Pass to `feature-developer`:
    - The plan
    - The requirements list
    - The current failing tests and the exact `/run-tests` invocations
- The `feature-developer` must implement in small, incremental steps.
- After each small step, the `feature-developer` must:
    1) Describe what changed (files, functions)
    2) Specify the smallest relevant `/run-tests` invocation to run now
- You MUST run that `/run-tests` invocation after each step.
- If tests fail:
    - Continue with minimal changes until green.
    - Only adjust tests by looping with `automation-qa` (tests-first) if the tests are genuinely wrong.
- Continue until all feature-related tests are green.

### 6) Broader testing & stabilization gate (MANDATORY) (delegate to `automation-qa`)

- This step is required. Do not proceed to Acceptance Review until it is completed.
- Re-invoke `automation-qa` and require it to return:
    - “Additional regression/integration tests needed?” (YES/NO + reasons)
    - A broader `/run-tests` invocation to run (reasonable scope; e.g., package-level)
    - A stabilization verdict: **PASS / PARTIAL / FAIL**
- You MUST:
    1) Run the broader `/run-tests` invocation and summarize the output
    2) If verdict is PARTIAL or FAIL, loop using strict TDD:
        - `automation-qa` updates/extends tests (RED)
        - Run `/run-tests` to confirm RED
        - `feature-developer` makes minimal changes (GREEN; run tests after each step)
        - Re-run the broader `/run-tests`
        - Re-run `automation-qa` for a new verdict
- If `automation-qa` cannot be invoked (quota/error), STOP and report the workflow is blocked.

### 7) Acceptance review (delegate to `acceptance-reviewer`)

- Provide `acceptance-reviewer`:
    - The original request (`$ARGUMENTS` and clarifications)
    - The plan from `plan-creator`
    - A summary of implementation + tests (including key `/run-tests` invocations)
    - Evidence from Step 6 (broader invocation + result summary + automation-qa verdict)
- Have the subagent:
    - Check whether all requirements are met
    - Produce a verdict: **PASS / PARTIAL / FAIL** with a requirements checklist
- If there are functional gaps:
    - Loop back using strict TDD:
        - `automation-qa` (tests first, RED)
        - run `/run-tests` to confirm RED
        - `feature-developer` (minimal implementation, GREEN with tests after each step)
        - stabilization gate (Step 6) as needed
        - re-run acceptance review

### 8) Refactoring (delegate to `refactorer`, with tests after each step)

- Once acceptance reasonably passes, invoke `refactorer` for behavior-preserving cleanup:
    - Improve structure, naming, separation of concerns
    - Remove duplication, clarify control flow
    - Keep external behavior identical
- The `refactorer` must follow a small-steps + tests loop:
    - Before each refactor step: state what will change and why
    - After each refactor step:
        - specify the smallest relevant `/run-tests` invocation
        - you MUST run it
        - if it fails, fix or revert
- If larger refactors are discovered:
    - Record them as follow-up tasks instead of doing them now.

### 9) Code review with reflection loop (delegate to `code-reviewer`)

- Invoke `code-reviewer` once refactoring is green.
- `code-reviewer` should evaluate:
    - Architecture alignment
    - Maintainability
    - Style
    - Test design quality
- Findings must be classified:
    - BLOCKING (must fix)
    - NON-BLOCKING (nice-to-have)
- For BLOCKING issues, apply a reflection loop:
    - Functional issue:
        - route to `automation-qa` (tests first, RED) + run `/run-tests`
        - then `feature-developer` (minimal fix, GREEN with tests after each step)
    - Structural/style/design issue:
        - route to `refactorer` (small refactor) + run `/run-tests` after each step
- Re-invoke `code-reviewer` after fixes.
- Repeat until no blocking issues remain, or the user explicitly accepts remaining trade-offs.

### 10) Update documentation (delegate to `documentation-updater`)

- Once code review has no blocking issues, invoke `documentation-updater` to update any documentation impacted by the change:
    - README usage examples
    - configuration/env var references
    - architecture notes / module boundaries
    - any runbooks that now drift
- Keep doc changes minimal and strictly tied to the implemented behavior.
- If documentation changes include any code changes (they usually should not), run an appropriate `/run-tests` once
  afterward.

The workflow-completion hook will generate the final summary when the workflow completes.

## Non-negotiable constraints

- TDD is mandatory:
    - tests before implementation
    - tests reviewed (tests-reviewer PASS) before implementation begins
    - after every implementation or refactor step, run the smallest relevant `/run-tests`
- Prefer narrow `/run-tests` invocations unless a broader run is required by the workflow.
- Do not introduce features beyond what the user requested in `$ARGUMENTS`.
