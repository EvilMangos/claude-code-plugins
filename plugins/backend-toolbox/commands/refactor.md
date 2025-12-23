---
description: Refactor code in a given path (file or folder) with tests after each step; never modify test files. If no path is provided, scope is the entire codebase.
argument-hint: [ path ]
allowed-tools: Read, Edit, Write, Grep, Glob, Bash(git:*), SlashCommand, Task
---

You are orchestrating a **refactor-only** workflow for this repository.

The user request is:

> $ARGUMENTS

The argument is an optional **path** to a file or folder. If no argument is provided, the scope is the **entire codebase
**.

You MUST follow the workflow strictly and delegate to the named subagents at each step.
Do not do a subagent's work in the main agent.

Required subagents:

- plan-creator
- refactorer
- code-reviewer
- acceptance-reviewer
- documentation-updater

## Hard constraints (non-negotiable)

1) **Do not modify test files** (read-only is fine).
    - You must NOT edit, create, delete, rename, or move any test file.
    - If a change would require updating tests, STOP and report that tests must be handled via the separate tests
      command.

   See `skills/test-best-practices/references/test-file-patterns.md` for complete test file identification patterns.
   Default patterns include: `/test/`, `/tests/`, `/__tests__/`, files containing `.spec.` or `.test.`, etc.

2) **Behavior-preserving refactor**
    - Do not change external behavior intentionally.
    - Prefer small, reversible steps.

3) **Tests after each step**
    - After **every refactor step** (each plan item that changes code), run tests with the smallest relevant scope.

## Preflight (main agent)

1) Determine scope:
    - If `$ARGUMENTS` is empty: set scope to the repo root (`.`).
    - Else: set scope to `$ARGUMENTS`.

2) Verify the scope exists:
    - Use Glob on the chosen scope.
    - If it does not exist, STOP and report the path is invalid.

3) Establish baseline:
    - Run tests with a narrow scope relevant to the refactor (or the smallest reasonable default if broad scope).
    - If baseline is failing, STOP and report that refactor is blocked until tests are green.

## Workflow

### 1) Clarify & high-level understanding (main agent)

- Restate the scope (path or entire codebase) and what “success” means:
    - behavior preserved
    - tests remain green
    - no test files changed
- Identify the main refactor goals appropriate to the scope:
    - readability, structure, coupling, naming, duplication, error-handling hygiene, performance footguns
- List explicit assumptions (only if needed). Do not guess repo rules if CLAUDE.md defines them.

### 2) Planning (delegate to `plan-creator`)

Invoke `plan-creator` to:

- Inspect the scope and surrounding dependencies.
- Propose a **small-step refactor plan** (steps should be independently testable).
- For each step, include:
    - files to change (must exclude test files)
    - expected outcome
    - the smallest relevant test scope to use after that step
- Include a “test-file safety” note: how the plan avoids touching tests.
- If scope is the entire codebase:
    - Prioritize the top 3–10 highest-value refactors; do not attempt a sweeping rewrite.

Adopt or lightly refine the plan to ensure:

- steps are small
- each step has a test command
- no step edits test files

### 3) Refactor (delegate to `refactorer`, tests after each step)

Pass the plan to `refactorer` and require:

For each plan step:

1) Make the minimal behavior-preserving changes.
2) State what changed (files/functions) and why.
3) Specify the smallest test scope to run now.
4) BEFORE moving to the next step, you MUST:
    - Run tests with the specified scope
    - Check changed files with `git diff --name-only`
    - If any touched file matches “test files/dirs” rules:
        - Revert those changes immediately (via git) and STOP with a report
        - Do not proceed further

If tests fail:

- Fix the refactor (or revert) with minimal changes, then re-run tests.
- Do not proceed until green.

### 4) Code review (delegate to `code-reviewer`; if not ok, loop to Planning)

Invoke `code-reviewer` with:

- the refactor plan
- what changed (high-level)
- the test commands run

**⛔ MANDATORY GATE - NO EXCEPTIONS, NO RATIONALIZATION:**

You MUST NOT proceed to Step 5 unless no BLOCKING issues remain.

- Do NOT rationalize skipping this gate ("issues are minor", "refactor is good", etc.)
- Do NOT use your own judgment to override this gate
- BLOCKING issues mean the loop MUST execute - no exceptions

```
LOOP while BLOCKING issues remain (max 5 iterations):
  IF code-reviewer reports BLOCKING issues:
    1. Invoke plan-creator to update the plan to address issues
    2. Invoke refactorer to apply fixes step-by-step with tests after each step
    3. Re-invoke code-reviewer
    4. Check for remaining BLOCKING issues
  END IF
END LOOP
```

**HARD STOP: Only proceed to Step 5 after no BLOCKING issues remain.**

### 5) Acceptance review (delegate to `acceptance-reviewer`; if not ok, loop to Planning)

Acceptance criteria for refactor work:

- behavior preserved (as evidenced by tests)
- no test files changed
- scope is reasonable for the provided scope (path or entire codebase)
- code quality improved per stated goals

**⛔ MANDATORY GATE - NO EXCEPTIONS, NO RATIONALIZATION:**

You MUST NOT proceed to Step 6 unless verdict == PASS.

- Do NOT rationalize skipping this gate ("mostly acceptable", "minor gaps", etc.)
- Do NOT use your own judgment to override this gate
- PARTIAL means the loop MUST execute - no exceptions

```
LOOP while acceptance verdict != PASS (max 5 iterations):
  IF verdict is PARTIAL or FAIL:
    1. Invoke plan-creator to propose minimal corrective steps
    2. Invoke refactorer to apply them with tests after each step
    3. Re-invoke acceptance-reviewer
    4. Check verdict again
  END IF
END LOOP
```

**HARD STOP: Only proceed to Step 6 after verdict == PASS.**

### 6) Update Documentation (delegate to `documentation-updater`)

Invoke `documentation-updater` to update documentation impacted by the refactor, while respecting:

- do not modify test files
- keep doc changes minimal and accurate
- update only what is now misleading (paths, module names, usage examples, architecture notes, etc.)

If doc updates include code changes, re-run tests once afterward.

The workflow-completion hook will generate the final summary when the workflow completes.
