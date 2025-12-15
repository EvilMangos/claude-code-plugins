---
name: validate-test-files
description: Validates that test files are not being modified inappropriately during refactor workflows
hooks:
  - event: PreToolUse
    tools: [Edit, Write]
---

# Test File Validation Hook

When the Edit or Write tool is about to modify a file, check if the file path matches test file patterns:

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
If the current agent is `feature-developer`:
- **BLOCK** modifications to test files
- Return message: "feature-developer cannot modify tests. Delegate to automation-qa agent."

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
