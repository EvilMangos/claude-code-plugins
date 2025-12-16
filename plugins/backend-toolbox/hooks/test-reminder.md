---
name: test-reminder
description: Reminds to run tests after code modifications
hooks:
  - event: PostToolUse
    tools: [Edit, Write]
---

# Test Reminder Hook

After any Edit or Write tool successfully modifies a source file, provide a reminder about running tests.

## When to Trigger

Trigger this reminder when:

- A production/source code file was modified (not a test file, not docs/config)
- The modification was successful

### What counts as “source code”

- Treat as **source** by default.
- Treat as **NOT source** if it matches any **Skip** rule below.

## Reminder Message

After code modification, include this reminder:

```
Remember: Run `/run-tests <relevant-path>` to verify your changes.
```

## Context-Aware Suggestions

### If in TDD workflow

```
TDD Checkpoint: Run the smallest relevant test command to verify:
- GREEN stage: tests should now pass
- REFACTOR stage: tests should still pass
```

### If modifying multiple files

```
Multiple files changed. Consider running tests after each logical change
to catch issues early.
```

## Skip Reminder When

- File is a test file (tests don't need test reminders)
- File is documentation (\*.md, docs/\*\*)
- File is configuration only (_.json, _.yaml, \*.toml)
- A test command was just run immediately before this reminder would be emitted

### Test file patterns (same as validate-test-files)

- Path contains: `/test/`, `/tests/`, `/__tests__/`, `/spec/`, `/specs/`, `/e2e/`, `/integration/`
- Path contains: `/cypress/`, `/playwright/`
- Filename contains: `.spec.`, `.test.`
- Filename ends with: `_test.`, `Test.`

### Deterministic “tests just ran” rule

Skip the reminder only if, in the immediately preceding assistant action/output, there is clear evidence that tests were run, for example:

- A `/run-tests ...` invocation was executed, or
- A test runner command was executed via Bash (e.g., `pytest`, `jest`, `go test`, `cargo test`, `npm test`, `pnpm test`, `yarn test`)

If unsure, default to emitting **one** gentle reminder (do not repeat reminders back-to-back without a new code change).
