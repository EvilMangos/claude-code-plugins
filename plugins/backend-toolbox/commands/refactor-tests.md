---
description: Refactor tests within an optional path (file or folder). If no path is provided, scope is the entire test suite. Never modify non-test production code.
argument-hint: [ path ]
allowed-tools: Read, Edit, Grep, Glob, Bash(git:*), Bash(ls:*), Bash(find:*), SlashCommand, Task
---

You are orchestrating a **tests-refactor-only** workflow for this repository.

The user request is:

> $ARGUMENTS

The argument is an optional **path** to a test file or test folder. If no argument is provided, the scope is the *
**entire test suite**.

You MUST follow the workflow strictly and delegate to the named subagents at each step.
Do not do a subagent's work in the main agent.

Required subagents:

- plan-creator
- automation-qa
- tests-reviewer
- code-reviewer
- acceptance-reviewer
- documentation-updater

## Hard constraints (non-negotiable)

1) **Tests-only changes**
   You may edit ONLY:
    - Test files / test folders (definitions below)
    - Test-only support files (definitions below)
    - Documentation files (for Step 6)

   You must NOT edit, create, delete, rename, or move **production code**.

2) **Behavior-preserving**
    - Do not intentionally change the meaning/coverage of the tests.
    - Refactor for readability, determinism, structure, and robustness.

3) **Tests after each step**
    - After **every refactor step** that changes files, run the smallest relevant `/run-tests` invocation.

### Test File Patterns

See `skills/test-best-practices/references/test-file-patterns.md` for complete identification patterns.

Key patterns:

- **Test files**: `/test/`, `/tests/`, `/__tests__/`, files containing `.spec.` or `.test.`
- **Support files**: `/__mocks__/`, `/fixtures/`, `/testdata/`, `/test_utils/`
- **Documentation**: `README*`, `CHANGELOG*`, `docs/**` (for Step 6 only)

If a required improvement would need production code changes, STOP and tell the user to use `/refactor` instead.

## Preflight (main agent)

The SessionStart hook verifies `/run-tests` exists.

1) Determine scope:

- If `$ARGUMENTS` is empty: scope = "entire test suite".
- Else: scope = `$ARGUMENTS`.

2) Validate scope path (if provided):

- Use Glob to confirm the path exists.
- If it does not exist, STOP and report the path is invalid.
- If it exists but does NOT look like a test file/folder by the definitions above, STOP and tell the user to use
  `/refactor`.

3) Establish baseline:

- Run the smallest reasonable `/run-tests` for the scope:
    - If a path was provided: `/run-tests $ARGUMENTS`
    - Else: `/run-tests` (or the smallest default suite your repo uses)
- If baseline fails, STOP: refactoring is blocked until tests are green.

## Workflow

### 1) Clarify & high-level understanding (main agent)

- Restate the scope (path or entire test suite) and success criteria:
    - tests remain green
    - no production code changed
    - improved readability/structure/determinism
- Identify the refactor goals (choose what is applicable):
    - reduce duplication
    - simplify setup/teardown
    - clarify naming and describe blocks
    - remove flakiness/time dependence
    - improve fixtures/helpers organization
    - speed up tests (avoid expensive setup where possible)

### 2) Planning (delegate to `plan-creator`)

Invoke `plan-creator` to:

- Inspect the test scope and its dependencies.
- Produce a **small-step refactor plan** (each step independently testable).
- For each step include:
    - files to change (must be tests/support/docs only)
    - expected outcome
    - exact smallest `/run-tests` invocation to run after the step
- If scope is the entire test suite:
    - prioritize top 3–10 highest-value refactors; no sweeping rewrite
- Add a “file-safety” section explaining how the plan avoids production code edits.

Adopt or lightly refine the plan to ensure:

- steps are small
- each step includes a test command
- file list stays within allowed areas

### 3) Refactor tests (delegate to `automation-qa`, tests after each step)

Delegate the plan to `automation-qa` and require it to execute steps one-by-one.

For each plan step, `automation-qa` must:

1) Apply minimal behavior-preserving edits (tests/support/docs only).
2) Describe what changed (files + why).
3) Provide the exact `/run-tests` invocation to run now (smallest scope).

You MUST, after each step:

- Run `/run-tests ...`
- Check changed files with `git diff --name-only`

If any changed file is NOT:

- a test file/folder, OR
- a test-only support file, OR
- a documentation file
  then:
- revert those changes immediately (via git)
- STOP and report which file violated scope.

If tests fail:

- `automation-qa` must fix the refactor (or revert) with minimal changes
- re-run the same `/run-tests` command
- do not proceed until green

### 4) Test quality review gate (delegate to `tests-reviewer`; if not ok, loop to Planning)

Invoke `tests-reviewer` with:

- the plan
- summary of changes
- the `/run-tests` commands run

`tests-reviewer` must return: **PASS / PARTIAL / FAIL**.

**⛔ MANDATORY GATE - NO EXCEPTIONS, NO RATIONALIZATION:**

You MUST NOT proceed to Step 5 unless verdict == PASS.

- Do NOT rationalize skipping this gate ("tests are adequate", "will fix later", etc.)
- Do NOT use your own judgment to override this gate
- PARTIAL means the loop MUST execute - no exceptions

```
LOOP while verdict != PASS (max 5 iterations):
  IF verdict is PARTIAL or FAIL:
    1. Invoke plan-creator to update the plan to address feedback
    2. Invoke automation-qa to apply fixes step-by-step with /run-tests after each step
    3. Re-invoke tests-reviewer
    4. Check verdict again
  END IF
END LOOP
```

**HARD STOP: Only proceed to Step 5 after verdict == PASS.**

### 5) Code review (delegate to `code-reviewer`; if not ok, loop to Planning)

Invoke `code-reviewer` with:

- plan + summary of changes + tests run

**⛔ MANDATORY GATE - NO EXCEPTIONS, NO RATIONALIZATION:**

You MUST NOT proceed to Step 6 unless no BLOCKING issues remain.

- Do NOT rationalize skipping this gate ("issues are minor", "code is acceptable", etc.)
- Do NOT use your own judgment to override this gate
- BLOCKING issues mean the loop MUST execute - no exceptions

```
LOOP while BLOCKING issues remain (max 5 iterations):
  IF code-reviewer reports BLOCKING issues:
    1. Invoke plan-creator to update the plan to address issues
    2. Invoke automation-qa to apply fixes step-by-step with /run-tests after each step
    3. Re-invoke code-reviewer
    4. Check for remaining BLOCKING issues
  END IF
END LOOP
```

**HARD STOP: Only proceed to Step 6 after no BLOCKING issues remain.**

### 6) Acceptance review (delegate to `acceptance-reviewer`; if not ok, loop to Planning)

Acceptance criteria for this command:

- Tests remain green (evidence via `/run-tests`)
- No production code changed (evidence via diff checks)
- Refactor scope stayed within the requested test scope
- Test code quality improved (structure/readability/determinism)

**⛔ MANDATORY GATE - NO EXCEPTIONS, NO RATIONALIZATION:**

You MUST NOT proceed to Step 7 unless verdict == PASS.

- Do NOT rationalize skipping this gate ("mostly acceptable", "minor gaps", etc.)
- Do NOT use your own judgment to override this gate
- PARTIAL means the loop MUST execute - no exceptions

```
LOOP while acceptance verdict != PASS (max 5 iterations):
  IF verdict is PARTIAL or FAIL:
    1. Invoke plan-creator to propose corrective steps
    2. Invoke automation-qa to apply fixes step-by-step with /run-tests after each step
    3. Re-invoke acceptance-reviewer
    4. Check verdict again
  END IF
END LOOP
```

**HARD STOP: Only proceed to Step 7 after verdict == PASS.**

### 7) Update Documentation (delegate to `documentation-updater`)

Invoke `documentation-updater` to update only docs impacted by the refactor (test conventions, how to run tests, fixture
locations, etc.).
The documentation-updater must not change production code.

After doc changes:

- Run an appropriate `/run-tests` once.

The workflow-completion hook will generate the final summary when the workflow completes.
