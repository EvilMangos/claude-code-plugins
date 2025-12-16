---
name: validate-test-files
description: Validates that test files are not being modified inappropriately during refactor workflows
hooks:
  - event: PreToolUse
    tools: [ Edit, Write ]
---

# Test File Validation Hook

When the Edit or Write tool is about to modify a file, check if the file path matches test file patterns:

## Context detection (deterministic + safe fallback)

These rules depend on knowing the current workflow and/or active agent.

Use this precedence order:

1. **Explicit workflow**: If the user explicitly invoked `/develop-feature`, `/refactor`, or `/refactor-tests` in the
   current session, treat that as the active workflow until another workflow command is invoked.
2. **Explicit agent**: If the system context identifies the active subagent (e.g., `backend-developer`,
   `automation-qa`), use it.
3. **Fallback**: If workflow/agent cannot be determined reliably, **do not BLOCK**. Instead, emit a WARNING explaining
   what would normally be blocked and ask the user to confirm intent.

## Test File Patterns

A file is a test file if ANY of these match:

- Path contains: `/test/`, `/tests/`, `/__tests__/`, `/spec/`, `/specs/`, `/e2e/`, `/integration/`
- Path contains: `/cypress/`, `/playwright/`
- Filename contains: `.spec.`, `.test.`
- Filename ends with: `_test.`, `Test.`

## Validation Rules

### During `/refactor` command

If the current workflow is a code refactor (not test refactor):

- **BLOCK** modifications to test files
- Return message: "Cannot modify test files during /refactor. Use /refactor-tests for test changes."

### During `/develop-feature` command

If the current agent is `backend-developer`:

- **BLOCK** modifications to test files
- Return message: "backend-developer cannot modify tests. Delegate to automation-qa agent."

### During `/refactor-tests` command

If the file is NOT a test file:

- **BLOCK** modifications
- Return message: "Cannot modify production code during /refactor-tests. Only test files allowed."

## Allowed Exceptions

- `automation-qa` agent can always modify test files
- `tests-reviewer` agent can modify test files when explicitly asked to "apply fixes"
- `refactorer` agent can modify test files ONLY to:
    - Reflect moved/renamed elements
    - Remove reliance on implementation details

## Warning fallback message (when context is unknown)

When you cannot determine workflow/agent reliably, return:

```
WARNING: Test file protection could not determine the active workflow/agent.
File: [target path]
Reason: This file looks like a test file (or non-test file) and might violate /refactor, /refactor-tests, or /develop-feature guardrails.
If you intend to proceed, confirm your workflow intent (e.g., “I am in /refactor-tests” or “delegate to automation-qa”).
```
