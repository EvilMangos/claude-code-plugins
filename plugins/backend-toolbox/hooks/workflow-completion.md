---
name: workflow-completion
description: Generates workflow summary when TDD commands complete
hooks:
  - event: Stop
---

# Workflow Completion Hook

When a TDD workflow command completes, generate a structured summary of what was accomplished.

## Applies To

Trigger summary for these commands:
- `/develop-feature`
- `/refactor`
- `/refactor-tests`

## Summary Templates

### For /develop-feature

```markdown
## Workflow Complete: Feature Development

**Feature:** [brief description from original request]

### What was implemented
- [key behavioral changes]
- [new functionality added]

### Files touched
- [list of modified/created files]

### Tests
- Added/Updated: [test file names]
- Run command: `/run-tests [relevant-path]`

### Review Outcomes
- Tests-reviewer: [PASS/PARTIAL/FAIL]
- Acceptance: [pass/partial/fail]
- Code-review: [X blocking, Y non-blocking]

### Documentation
- [what documentation was updated, if any]

### Follow-up
- [deferred tasks or future improvements identified]
```

### For /refactor

```markdown
## Workflow Complete: Refactor

**Scope:** [path or "entire codebase"]
**Goals:** [what was improved - structure, coupling, naming, etc.]

### Files changed
- [explicit list of modified files]

### Confirmation
- No test files changed
- Tests green after each step

### Test commands used
- [list of /run-tests invocations]

### Key improvements
- [structural changes made]
- [design improvements]

### Follow-up
- [deferred refactors for separate tasks]
```

### For /refactor-tests

```markdown
## Workflow Complete: Test Refactor

**Scope:** [path or "entire test suite"]
**Goals:** [what was improved - readability, determinism, structure, etc.]

### Files changed
- [explicit list of modified test files]

### Confirmation
- No production code changed
- Tests green after each step

### Test commands used
- [list of /run-tests invocations]

### Key improvements
- [readability improvements]
- [determinism fixes]
- [structural changes]

### Follow-up
- [suggestions for future test improvements]
```

## When NOT to Trigger

Do not generate summary when:
- Session ends without completing a workflow command
- User interrupts mid-workflow
- An error caused the workflow to abort
- Simple queries or non-workflow commands were used

## Summary Placement

The summary should be the final output before the session ends, providing a clear record of what was accomplished during the TDD workflow.
