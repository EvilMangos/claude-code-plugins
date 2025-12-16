---
name: tdd-workflow
description: >
  This skill should be used when the user asks to "use TDD", "write tests first", "follow red-green-refactor",
  "test-driven development", "TDD workflow", "write failing test first", "do TDD", "red-green-refactor cycle",
  or explicitly requests a test-first development approach for implementing features.
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

## Phase Transition Rules

### RED → GREEN

Move to GREEN only when:

- Test compiles/runs
- Test fails for the right reason
- Failure message is clear

### GREEN → REFACTOR

Move to REFACTOR only when:

- All tests pass
- Implementation is minimal
- No known bugs

### REFACTOR → RED (Next Cycle)

Move to next RED phase only when:

- All tests still pass
- Code quality is acceptable
- No pending refactoring needed

## Common TDD Anti-Patterns

| Anti-Pattern                       | Why It's Problematic                             |
|------------------------------------|--------------------------------------------------|
| Writing tests after implementation | Loses design benefits of TDD                     |
| Testing too much at once           | Makes failures hard to diagnose                  |
| Skipping RED phase                 | Tests may match implementation, not requirements |
| Skipping REFACTOR phase            | Accumulates technical debt                       |
| Large refactor steps               | Hard to identify what broke tests                |
| Adding untested functionality      | Violates TDD principles                          |

## Additional Resources

### Reference Files

For detailed guidance, consult:

- **`references/phase-checklists.md`** - Quality checklists for each TDD phase

### Examples

Working examples in `examples/`:

- **`examples/typescript-tdd-example.md`** - Step-by-step TDD walkthrough building from scratch

### Related Skills

For testing patterns, mocking strategies, and test quality guidance, see the `test-best-practices` skill.
