---
name: workflow-completion
description: Generates workflow summary when TDD commands complete
hooks:
  - event: Stop
---

# Workflow Completion Hook

When a TDD workflow command completes, generate a structured summary by reading from `.workflow/` files.

## Applies To

Trigger summary for these commands:

- `/develop-feature`
- `/refactor`
- `/refactor-tests`
- `/fix-bug`
- `/devops-change`

## Detection

Check if `.workflow/metadata.json` exists and has `"status": "completed"`.

If the workflow directory exists but status is not completed, the workflow was interrupted - report partial progress.

## Summary Generation

Read the relevant `.workflow/*.md` files to compile the summary:

### For /develop-feature

Read these files to extract information:
- `.workflow/00-requirements.md` - Feature name and requirements
- `.workflow/01-plan.md` - Implementation plan
- `.workflow/04-implementation.md` - Files modified, tests passing
- `.workflow/06-acceptance.md` - Acceptance verdict
- `.workflow/07-performance.md` - Performance verdict
- `.workflow/08-security.md` - Security verdict
- `.workflow/10-code-review.md` - Code review verdict
- `.workflow/11-documentation.md` - Documentation updates

Generate:

```markdown
## Workflow Complete: Feature Development

**Feature:** [from 00-requirements.md]

### What was implemented

- [from 04-implementation.md Summary section]

### Files touched

- [from 04-implementation.md Files Modified section]

### Tests

- [from 02-tests-design.md - test files and count]
- Run command: [from 04-implementation.md]

### Review Outcomes

| Review | Verdict |
|--------|---------|
| Tests-reviewer | [from 03-tests-review.md] |
| Acceptance | [from 06-acceptance.md] |
| Performance | [from 07-performance.md] |
| Security | [from 08-security.md] |
| Code-review | [from 10-code-review.md] |

### Documentation

- [from 11-documentation.md]

### Follow-up

- [from 09-refactoring.md Follow-up Tasks section]
- [any NON-BLOCKING issues from reviews]
```

### For /refactor

Read:
- `.workflow/00-requirements.md` - Refactoring scope
- `.workflow/09-refactoring.md` - Changes made

Generate:

```markdown
## Workflow Complete: Refactor

**Scope:** [from 00-requirements.md]
**Goals:** [from 00-requirements.md]

### Files changed

- [from 09-refactoring.md Files Modified section]

### Confirmation

- No test files changed (behavior preserved)
- Tests green after each step

### Test commands used

- [from 09-refactoring.md Refactoring Log - test runs]

### Key improvements

- [from 09-refactoring.md Summary section]

### Follow-up

- [from 09-refactoring.md Follow-up Tasks section]
```

### For /refactor-tests

Read:
- `.workflow/00-requirements.md` - Test refactoring scope
- `.workflow/02-tests-design.md` - Test changes

Generate:

```markdown
## Workflow Complete: Test Refactor

**Scope:** [from 00-requirements.md]
**Goals:** [from 00-requirements.md]

### Files changed

- [from workflow files - test file modifications]

### Confirmation

- No production code changed
- Tests green after each step

### Key improvements

- [readability, determinism, structure improvements]

### Follow-up

- [suggestions for future test improvements]
```

### For /fix-bug

Read:
- `.workflow/00-requirements.md` - Bug description
- `.workflow/04-implementation.md` - Fix details

Generate:

```markdown
## Workflow Complete: Bug Fix

**Bug:** [from 00-requirements.md]
**Root cause:** [from implementation notes]

### Fix applied

- [from 04-implementation.md]

### Files modified

- [list from workflow files]

### Tests

- Regression test added: [test name/location]
- All tests passing

### Verification

- [how the fix was verified]
```

## Cleanup Option

After generating the summary, offer to clean up:

```
Workflow artifacts are in `.workflow/`. Would you like to:
- Keep them for reference
- Delete them (rm -rf .workflow/)
```

## When NOT to Trigger

Do not generate summary when:

- `.workflow/metadata.json` doesn't exist
- Session ends without completing a workflow command
- User interrupts mid-workflow (status != "completed")
- Simple queries or non-workflow commands were used

## Partial Progress Report

If `.workflow/` exists but workflow is incomplete, report:

```markdown
## Workflow Interrupted

**Feature:** [from metadata.json or 00-requirements.md]
**Last completed step:** [highest numbered file in .workflow/]

### Progress so far

- [list completed steps based on existing files]

### To resume

The workflow state is preserved in `.workflow/`. You can:
- Continue from where you left off
- Start fresh with `rm -rf .workflow/` and re-run the command
```
