---
description: Develop a backend feature end-to-end using strict TDD with planning, test design, test review gate, implementation, QA, acceptance review, refactoring, and code review subagents.
argument-hint: [feature-description]
allowed-tools: Read, Grep, Glob, Task, SlashCommand, Bash(pytest:*)
---

You are orchestrating a multistep **TDD** feature workflow for this repository.

The user request is:

> $ARGUMENTS

You MUST follow this workflow strictly and delegate to the named subagents at each step.
Do not do a subagent's work in the main agent.

1. **Clarify & high-level understanding (main agent)**
    - Restate the feature in your own words.
    - Identify affected domains/packages (e.g., job-agent-backend, telegram_bot, jobs-repository).
    - If anything is ambiguous, list assumptions explicitly.
    - Derive a list of **behavioral requirements** (inputs, outputs, edge cases).

2. **Planning (delegate to `plan-creator` subagent)**
    - Explicitly invoke the `plan-creator` subagent to:
        - Explore the relevant code.
        - Produce a step-by-step implementation and testing plan.
        - Map each requirement to concrete code areas and test locations.
        - Highlight risks and open questions.
    - Wait for the subagent's response, then adopt or lightly refine that plan.
    - Ensure the plan clearly separates:
        - **Test steps** (what tests to write/update, where).
        - **Implementation steps** (what logic to add/change, where).

3. **TDD – Test design & RED stage (delegate to `automation-qa` subagent)**
    - Before changing any implementation, invoke the `automation-qa` subagent to:
        - Design and write/update tests for the planned behavior:
            - Normal paths.
            - Edge cases.
            - Error conditions.
        - Place tests in the appropriate `*_test.py` files and fixtures.
        - Provide **exact pytest commands** to run just these tests (smallest scope).
    - After tests are created/updated, run the suggested pytest commands against the **current** implementation to
      confirm they **fail** (RED).
    - If tests pass unexpectedly, work with `automation-qa` to:
        - Strengthen expectations, or
        - Adjust scenarios so that they properly capture the new behavior.

4. **Test quality review gate (delegate to `tests-reviewer` subagent)**
    - Immediately after the RED stage, invoke the `tests-reviewer` subagent to review:
        - Requirements → tests mapping completeness.
        - Correctness: tests verify the *right* observable behavior.
        - Strength: assertions would fail for realistic bugs (avoid false positives).
        - Determinism & flake risk.
    - The `tests-reviewer` must return a **pass / partial / fail** verdict.
    - If verdict is **partial/fail**, loop back to `automation-qa` to tighten/fix tests and re-run the RED command, then
      re-run `tests-reviewer`.
    - Do not proceed to implementation until `tests-reviewer` verdict is **pass**.

5. **TDD – Implementation & GREEN stage (delegate to `feature-developer` subagent)**
    - Pass the plan, requirements, and current test state to the `feature-developer` subagent.
    - The `feature-developer` must:
        - Implement the feature in **small, incremental steps**.
        - After **each small step**:
            1. Describe what changed (files, functions).
            2. Run the **smallest relevant subset of tests** (usually the tests added/updated in step 3).
            3. If tests fail, fix the implementation (or adjust tests together with `automation-qa` if they were wrong)
               before proceeding.
    - This loop must continue until:
        - All tests related to this feature are **green**.
    - Do **not** perform large batches of implementation without running tests.
    - Keep scope limited strictly to the plan and the user request.

6. **Broader Testing & Stabilization gate (MANDATORY) (delegate to `automation-qa`)**

- This step is required. Do not proceed to Acceptance Review until it is completed.
- Re-invoke `automation-qa` and require it to return:
    - “Additional regression/integration tests needed?” (yes/no + reasons)
    - A broader test command to run (reasonable scope; e.g., package-level)
    - A stabilization verdict: PASS / PARTIAL / FAIL

- You MUST:
    1) Run the broader test command it recommends and paste the command + output summary.
    2) If verdict is PARTIAL or FAIL, loop using TDD:
        - `automation-qa` updates/extends tests (RED)
        - `feature-developer` makes minimal changes (GREEN; run tests after each step)
        - Re-run the broader test command
        - Re-run `automation-qa` for a new verdict

- If `automation-qa` cannot be invoked (quota/error), STOP and report the workflow is blocked.
  Do not “fill in” by doing QA judgment yourself.


7. **Acceptance review (delegate to `acceptance-reviewer` subagent)**
    - Provide the `acceptance-reviewer` subagent with:
        - The original request (`$ARGUMENTS` and clarifications).
        - The plan from `plan-creator`.
        - A summary of the implementation and tests (including key pytest commands).
    - Have the subagent:
        - Check whether all requirements are met.
        - Produce a pass/partial/fail verdict with a requirements checklist.
    - If there are **functional gaps**, loop back to:
        - `feature-developer` (for implementation changes), and
        - `automation-qa` (for additional tests),
          always using TDD (tests first, tests after each implementation step) until acceptance can reasonably pass.
    - If Step 6 evidence (broader command + result + automation-qa verdict) is missing, STOP and do not invoke
      `acceptance-reviewer`.

8. **Refactoring (delegate to `refactorer` subagent, with tests after each step)**
    - Once acceptance reasonably passes, invoke the `refactorer` subagent to perform **behavior-preserving cleanup**:
        - Improve structure, naming, and separation of concerns.
        - Remove duplication and clarify control flow.
        - Keep external behavior identical.
    - The refactorer must follow a **small-steps + tests** loop:
        - Before a refactor step: state what will change and why.
        - After each refactor step:
            1. Run the relevant narrow test subset (at least the feature-specific tests).
            2. If tests fail, fix the refactor or revert the change.
    - If the refactorer discovers larger refactor opportunities that are too big for this feature flow:
        - Note them explicitly as follow-up tasks instead of doing them now.

9. **Code review with reflection loop (delegate to `code-reviewer` subagent)**
    - Invoke the `code-reviewer` subagent once refactoring passes its local tests.
    - The `code-reviewer` should:
        - Evaluate architecture alignment, maintainability, style, and test design quality.
        - Classify findings into:
            - **Blocking issues** (must be fixed).
            - **Non-blocking suggestions** (nice-to-have).
    - For **blocking issues**, apply a **reflection loop**:
        - If the issue is **functional**:
            - Route it back to `feature-developer` + `automation-qa`:
                - Update tests first if needed (RED).
                - Adjust implementation.
                - Run tests after each step (GREEN).
        - If the issue is **structural / style / design**:
            - Route it back to `refactorer`:
                - Plan a small refactor step.
                - Apply it.
                - Run the relevant tests after each refactor step.
        - After fixes + tests are done, re-invoke `code-reviewer` to reassess.
    - Repeat this reflection loop (refactor ↔ code-reviewer, with tests after each change) until:
        - No blocking issues remain, or
        - Remaining issues are explicitly accepted as trade-offs by the user.

10. **Final report (main agent)**

- Summarize for the user:
    - What was implemented.
    - Files and modules touched.
    - Tests added/updated (with exact commands to run them).
    - Acceptance-review verdict and any remaining known limitations.
    - Refactoring highlights (what was improved structurally).
    - Code-review outcome (any remaining non-blocking suggestions).
    - Any follow-up work you recommend (separate tasks: additional features, broader refactors, extra tests).

Important constraints:

- **TDD is mandatory** for this command:
    - Tests are written/updated **before** implementation.
    - Tests are reviewed by `tests-reviewer` before implementation begins.
    - After **every implementation or refactor step**, run the smallest relevant subset of tests.
- Always respect each subagent's permissions and scope.
- Prefer narrow test commands (single file or package) over broad runs, unless explicitly needed.
- Do not introduce new features beyond what the user requested in `$ARGUMENTS`.
