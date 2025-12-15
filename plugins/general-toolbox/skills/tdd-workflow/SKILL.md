---
name: tdd-workflow
description: >
  This skill should be used when the user asks to "follow TDD", "write tests first",
  "use test-driven development", "RED-GREEN-REFACTOR", "test-first approach",
  "add tests before code", or needs guidance on proper TDD workflow and principles.
---

# TDD Workflow Guide

Test-Driven Development follows a strict three-phase cycle that drives design through tests.

## The RED-GREEN-REFACTOR Cycle

### 1. RED Phase (Write Failing Tests)

Write tests **before** implementation:
- Express behavioral requirements clearly in test names
- Verify tests fail for the **right reason** (missing functionality, not setup errors)
- Test observable outcomes, not internals
- Run tests to confirm expected failure

### 2. GREEN Phase (Minimal Implementation)

Write the **minimum code** to make tests pass:
- Add no features beyond what tests require
- Focus on correctness, not elegance
- Run tests after each small change
- Follow existing architecture patterns

### 3. REFACTOR Phase (Improve Design)

Improve code structure **without changing behavior**:
- Take small, reversible steps only
- Run tests after **every** refactor step
- If tests fail, revert and try a smaller step
- Eliminate duplication, improve readability

## Test Quality Principles

### Test Observable Behavior

**Verify:**
- Return values and API responses
- Persisted state changes
- Emitted events/messages
- Error conditions

**Avoid testing:**
- Internal method calls
- Private implementation details
- Exact query strings (unless contractual)
- Call ordering (unless contractual)

### Coverage Requirements

Cover every behavioral requirement:
- **Normal paths** - expected inputs produce expected outputs
- **Edge cases** - boundary values, empty collections, nulls
- **Error paths** - invalid inputs, failure conditions, timeouts

### Test Independence

- Ensure no dependency on execution order
- Set up required state within each test
- Clean up after tests (DB, files, env vars)
- Use controlled time/randomness for determinism

## Common Anti-Patterns

| Anti-Pattern | Why It's Problematic |
|--------------|---------------------|
| Writing tests after implementation | Loses design benefits of TDD |
| Testing too much at once | Makes failures hard to diagnose |
| Over-mocking | Tests pass but don't verify real behavior |
| Skipping refactor phase | Accumulates technical debt |
| Large refactor steps | Hard to identify what broke tests |

## Additional Resources

### Reference Files

For detailed guidance, consult:
- **`references/phase-checklists.md`** - Quality checklists for each TDD phase
- **`references/testing-patterns.md`** - Common testing patterns and examples

### Examples

Working examples in `examples/`:
- **`examples/typescript-tdd-example.md`** - Step-by-step TDD walkthrough
