# Test File Identification Patterns

Common patterns are used to identify test files across any codebase.

## Test File Locations (Path Segments)

Files in these directories are considered test files:

- `/test/`, `/tests/`
- `/__tests__/`
- `/spec/`, `/specs/`
- `/e2e/`, `/integration/`
- `/cypress/`, `/playwright/`
- `/integration-tests/`

## Test File Naming Conventions

Files matching these patterns are considered test files:

### By Substring

- Contains `.spec.` (e.g., `user.spec.ts`, `api.spec.js`)
- Contains `.test.` (e.g., `user.test.ts`, `api.test.js`)

### By Suffix

- Ends with `_test.*` (e.g., `user_test.go`, `api_test.py`)
- Starts with `Test*.*` (e.g., `TestUser.java`, `TestApi.cs`)
- Ends with `Tests.*` (e.g., `UserTests.java`, `ApiTests.cs`)

## Test-Only Support Files

These are allowed to be modified when refactoring tests, but are NOT production code:

### Directory Patterns

- `/__mocks__/`, `/mocks/`
- `/fixtures/`, `/testdata/`
- `/test_utils/`, `/testutils/`
- `/test_helpers/`, `/test-helpers/`
- `/testing/`
- `/testhelpers/`
- `/fakes/`, `/stubs/`

### File Patterns

- `conftest.py`, `conftest*.py` (pytest)
- `test_utils.*`, `testutils.*`
- `test_helpers.*`, `testhelpers.*`
- `*_test_helper.*`
- `*.mock.*`, `*.fake.*`, `*.stub.*`
- `setup_test.*`, `teardown_test.*`

## Language-Specific Conventions

### JavaScript/TypeScript

- `*.test.ts`, `*.spec.ts`, `*.test.tsx`, `*.spec.tsx`
- `*.test.js`, `*.spec.js`, `*.test.jsx`, `*.spec.jsx`
- `__tests__/` directory (Jest convention)
- `*.cy.ts`, `*.cy.js` (Cypress)
- `*.spec.ts` in `e2e/` (Playwright)

### Python

- `test_*.py` (pytest convention)
- `*_test.py` (pytest convention)
- `tests/` directory
- `conftest.py` (pytest fixtures)

### Go

- `*_test.go` (Go convention)
- Tests live in same package as code
- `testdata/` directory for fixtures

### Rust

- `#[cfg(test)]` modules (inline tests)
- `tests/` directory (integration tests)
- `benches/` directory (benchmarks)

### Java/Kotlin

- `*Test.java`, `*Tests.java`
- `*Spec.java`, `*Specs.java`
- `src/test/` directory (Maven/Gradle)
- `*Test.kt`, `*Tests.kt`

### Ruby

- `*_spec.rb` (RSpec)
- `*_test.rb` (Minitest)
- `spec/` directory

### C#

- `*Tests.cs`, `*Test.cs`
- `tests/` or `*.Tests/` project

## Detection Logic

A file can be determined to be a test file as follows:

```
1. Check if any path segment matches test directory patterns
2. Check if filename matches test naming patterns
3. If either matches, it's a test file

is_test_file(path):
  segments = path.split('/')
  filename = segments[-1]

  # Check directory patterns
  for segment in segments:
    if segment in ['test', 'tests', '__tests__', 'spec', 'specs',
                   'e2e', 'integration', 'cypress', 'playwright']:
      return True

  # Check filename patterns
  if '.spec.' in filename or '.test.' in filename:
    return True
  if filename.endswith('_test.go') or filename.endswith('_test.py'):
    return True
  if filename.startswith('Test') and filename.endswith('.java'):
    return True

  return False
```

## Usage in Commands

This reference is used by:

- `/refactor` - To ensure test files are not modified
- `/refactor-tests` - To ensure only test files are modified
- `automation-qa` agent - To identify where tests should be placed
- `tests-reviewer` agent - To validate test file organization
