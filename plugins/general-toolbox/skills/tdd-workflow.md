---
name: tdd-workflow
description: >
  Use when following TDD practices, understanding RED-GREEN-REFACTOR cycle, or ensuring test-first development.
  Comprehensive guide to Test-Driven Development workflow and principles.
---

# TDD Workflow Guide

## The RED-GREEN-REFACTOR Cycle

TDD follows a strict three-phase cycle:

### 1. RED Phase (Write Failing Tests)

- Write tests **before** implementation
- Tests must fail for the **right reason** (missing functionality, not setup errors)
- Tests should express **behavioral requirements** clearly
- Run tests to confirm they fail as expected

**Quality checks for RED phase:**
- Does the test name describe the expected behavior?
- Is the assertion testing observable outcomes (not internals)?
- Would this test catch real bugs?

### 2. GREEN Phase (Minimal Implementation)

- Write the **minimum code** to make tests pass
- Do not add features beyond what tests require
- Focus on correctness, not elegance
- Run tests after each small change

**Quality checks for GREEN phase:**
- All tests pass
- No new functionality beyond test requirements
- Implementation follows architecture rules

### 3. REFACTOR Phase (Improve Design)

- Improve code structure **without changing behavior**
- Small, reversible steps only
- Run tests after **every** refactor step
- If tests fail, revert and try a smaller step

**Quality checks for REFACTOR phase:**
- All tests still pass
- No behavior changes (tests are the spec)
- Code is cleaner, more readable, less duplicated

## Test Quality Principles

### Test Observable Behavior

Good tests verify:
- Return values
- Persisted state changes
- Emitted events/messages
- API responses
- Error conditions

Bad tests verify:
- Internal method calls
- Private implementation details
- Exact query strings (unless contractual)
- Call ordering (unless contractual)

### Coverage Requirements

Every behavioral requirement needs tests for:
- **Normal paths** - expected inputs produce expected outputs
- **Edge cases** - boundary values, empty collections, nulls
- **Error paths** - invalid inputs, failure conditions, timeouts

### Test Independence

- Tests should not depend on execution order
- Each test should set up its own state
- Clean up after tests (DB, files, env vars)
- Use controlled time/randomness for determinism

## Workflow Commands

```bash
# Run smallest relevant test subset
/run-tests <path-or-pattern>

# Example: Run tests for a specific module
/run-tests tests/unit/auth/

# Example: Run a single test file
/run-tests tests/unit/auth/test_login.py
```

## Common Anti-Patterns

1. **Writing tests after implementation** - Loses the design benefits of TDD
2. **Testing too much at once** - Makes failures hard to diagnose
3. **Over-mocking** - Tests pass but don't verify real behavior
4. **Skipping refactor phase** - Accumulates technical debt
5. **Large refactor steps** - Hard to identify what broke tests
