---
name: workflow-completion
description: Generates workflow summary when TDD commands complete
hooks:
  - event: Stop
---

# Workflow Completion Hook

When a TDD workflow command completes, generate a structured summary by reading from workflow files.

## Applies To

Trigger summary for these commands:

- `/develop-feature`
- `/refactor`
- `/refactor-tests`
- `/fix-bug`
- `/devops-change`

## Detection (Multi-Instance Aware)

Workflows are stored in subdirectories under `.workflow/`:

```
.workflow/
├── develop-feature-user-auth-1702834567/
│   └── metadata.json
├── fix-bug-login-timeout-1702834890/
│   └── metadata.json
└── .gitignore
```

### Step 1: Find Workflow Directories

List all subdirectories in `.workflow/`:
```bash
ls -d .workflow/*/ 2>/dev/null
```

### Step 2: Check Each for Completion

For each subdirectory, check if `metadata.json` exists and has `"status": "completed"`:
```bash
cat .workflow/{task-id}/metadata.json
```

### Step 3: Generate Summary for Completed Workflows

For each completed workflow, generate the appropriate summary based on the `command` field in `metadata.json`.

If a workflow directory exists but status is not "completed", the workflow was interrupted - report partial progress.

## Summary Generation

Read the relevant `{WORKFLOW_DIR}/*.md` files to compile the summary (where `WORKFLOW_DIR = .workflow/{task-id}`):

### For /develop-feature

Read these files to extract information:
- `{WORKFLOW_DIR}/00-requirements.md` - Feature name and requirements
- `{WORKFLOW_DIR}/01-plan.md` - Implementation plan
- `{WORKFLOW_DIR}/04-implementation.md` - Files modified, tests passing
- `{WORKFLOW_DIR}/06-acceptance.md` - Acceptance verdict
- `{WORKFLOW_DIR}/07-performance.md` - Performance verdict
- `{WORKFLOW_DIR}/08-security.md` - Security verdict
- `{WORKFLOW_DIR}/10-code-review.md` - Code review verdict
- `{WORKFLOW_DIR}/11-documentation.md` - Documentation updates

Generate:

```markdown
## Workflow Complete: Feature Development

**Task ID:** [from metadata.json]
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
- `{WORKFLOW_DIR}/00-requirements.md` - Refactoring scope
- `{WORKFLOW_DIR}/09-refactoring.md` - Changes made

Generate:

```markdown
## Workflow Complete: Refactor

**Task ID:** [from metadata.json]
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
- `{WORKFLOW_DIR}/00-requirements.md` - Test refactoring scope
- `{WORKFLOW_DIR}/02-tests-design.md` - Test changes

Generate:

```markdown
## Workflow Complete: Test Refactor

**Task ID:** [from metadata.json]
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
- `{WORKFLOW_DIR}/00-requirements.md` - Bug description
- `{WORKFLOW_DIR}/04-implementation.md` - Fix details

Generate:

```markdown
## Workflow Complete: Bug Fix

**Task ID:** [from metadata.json]
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
Workflow artifacts are in `{WORKFLOW_DIR}/`. Would you like to:
- Keep them for reference
- Delete this workflow only (rm -rf {WORKFLOW_DIR}/)
- Delete all completed workflows (finds all with status: completed)
```

## When NOT to Trigger

Do not generate summary when:

- No workflow subdirectories exist in `.workflow/`
- No `metadata.json` files found in subdirectories
- Session ends without completing a workflow command
- User interrupts mid-workflow (status != "completed")
- Simple queries or non-workflow commands were used

## Partial Progress Report

If a workflow directory exists but workflow is incomplete, report:

```markdown
## Workflow Interrupted

**Task ID:** [from metadata.json]
**Feature:** [from metadata.json or 00-requirements.md]
**Last completed step:** [highest numbered file in {WORKFLOW_DIR}/]

### Progress so far

- [list completed steps based on existing files]

### To resume

The workflow state is preserved in `{WORKFLOW_DIR}/`. You can:
- Continue from where you left off
- Start fresh with `rm -rf {WORKFLOW_DIR}/` and re-run the command
```

## Multiple Workflows

If multiple workflow directories exist, report each separately:

```markdown
## Workflow Status Summary

Found {N} workflow(s) in `.workflow/`:

### Completed
- `develop-feature-user-auth-1702834567` - User Authentication (completed)
- `fix-bug-login-timeout-1702834890` - Login Timeout Fix (completed)

### In Progress
- `develop-feature-payment-1702835012` - Payment Integration (step 4/12)

### Interrupted
- `refactor-api-1702830000` - API Refactor (interrupted at step 3)
```

For completed workflows, generate individual summaries. For in-progress or interrupted workflows, show status only.
