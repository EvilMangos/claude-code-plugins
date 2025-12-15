---
name: session-start
description: Verifies workflow prerequisites at session start
hooks:
  - event: SessionStart
---

# Session Start Hook

Checks for required project configuration when a session begins.

## Verification

When session starts, check for `/run-tests` command:
- Look for `.claude/commands/run-tests.md` in the target project

## Message Format

If `/run-tests` is missing:

```
Workflow Prerequisite Check

The general-toolbox workflows (develop-feature, refactor, refactor-tests) require a /run-tests command.

To set up:
1. Create `.claude/commands/run-tests.md` in your project
2. Wrap your test runner (pytest, jest, go test, cargo test, etc.)
3. Accept optional path/pattern arguments

Example run-tests.md:
---
description: Run tests
argument-hint: [path-or-pattern]
allowed-tools: Bash
---
Run the project's test suite with: `npm test $ARGUMENTS` (or your test command)

Once configured, /run-tests should work like:
- /run-tests (run all tests)
- /run-tests src/auth/ (run tests for auth module)
- /run-tests --filter=login (run filtered tests)
```

If `/run-tests` is present:

```
/run-tests command found - TDD workflows ready
```

## Silent Mode

If the target project is not a software project (no tests expected), this hook should not produce output. Detect this by:
- No `package.json`, `Cargo.toml`, `go.mod`, `pyproject.toml`, `Gemfile`, etc.
- No source code directories (`src/`, `lib/`, `app/`, etc.)
