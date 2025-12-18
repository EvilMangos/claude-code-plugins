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
- `{WORKFLOW_DIR}/requirements.md` - Feature name and requirements
- `{WORKFLOW_DIR}/plan.md` - Implementation plan
- `{WORKFLOW_DIR}/implementation.md` - Files modified, tests passing
- `{WORKFLOW_DIR}/acceptance.md` - Acceptance verdict
- `{WORKFLOW_DIR}/performance.md` - Performance verdict
- `{WORKFLOW_DIR}/security.md` - Security verdict
- `{WORKFLOW_DIR}/code-review.md` - Code review verdict
- `{WORKFLOW_DIR}/documentation.md` - Documentation updates

Generate:

```markdown
## Workflow Complete: Feature Development

**Task ID:** [from metadata.json]
**Feature:** [from requirements.md]

### What was implemented

- [from implementation.md Summary section]

### Files touched

- [from implementation.md Files Modified section]

### Tests

- [from tests-design.md - test files and count]
- Run command: [from implementation.md]

### Review Outcomes

| Review | Verdict |
|--------|---------|
| Tests-reviewer | [from tests-review.md] |
| Acceptance | [from acceptance.md] |
| Performance | [from performance.md] |
| Security | [from security.md] |
| Code-review | [from code-review.md] |

### Documentation

- [from documentation.md]

### Follow-up

- [from refactoring.md Follow-up Tasks section]
- [any NON-BLOCKING issues from reviews]
```

### For /refactor

Read:
- `{WORKFLOW_DIR}/requirements.md` - Refactoring scope
- `{WORKFLOW_DIR}/refactoring.md` - Changes made

Generate:

```markdown
## Workflow Complete: Refactor

**Task ID:** [from metadata.json]
**Scope:** [from requirements.md]
**Goals:** [from requirements.md]

### Files changed

- [from refactoring.md Files Modified section]

### Confirmation

- No test files changed (behavior preserved)
- Tests green after each step

### Test commands used

- [from refactoring.md Refactoring Log - test runs]

### Key improvements

- [from refactoring.md Summary section]

### Follow-up

- [from refactoring.md Follow-up Tasks section]
```

### For /refactor-tests

Read:
- `{WORKFLOW_DIR}/requirements.md` - Test refactoring scope
- `{WORKFLOW_DIR}/tests-design.md` - Test changes

Generate:

```markdown
## Workflow Complete: Test Refactor

**Task ID:** [from metadata.json]
**Scope:** [from requirements.md]
**Goals:** [from requirements.md]

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
- `{WORKFLOW_DIR}/requirements.md` - Bug description
- `{WORKFLOW_DIR}/implementation.md` - Fix details

Generate:

```markdown
## Workflow Complete: Bug Fix

**Task ID:** [from metadata.json]
**Bug:** [from requirements.md]
**Root cause:** [from implementation notes]

### Fix applied

- [from implementation.md]

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
**Feature:** [from metadata.json or requirements.md]
**Last completed step:** [from metadata.json current_step field]

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
