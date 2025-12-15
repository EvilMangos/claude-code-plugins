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
- A production/source code file was modified (not a test file, not docs)
- The modification was successful

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
- File is documentation (*.md, docs/**)
- File is configuration only (*.json, *.yaml, *.toml)
- A test command was just run in the previous step
