# TDD Phase Checklists

Detailed quality checklists for each phase of the RED-GREEN-REFACTOR cycle.

## RED Phase Checklist

Before moving to GREEN, verify:

### Test Quality

- [ ] Test name describes expected behavior clearly
- [ ] Test follows Arrange-Act-Assert (AAA) pattern
- [ ] Assertion tests observable outcomes, not implementation details
- [ ] Test would catch real bugs if implementation regressed

### Failure Verification

- [ ] Test fails when run
- [ ] Failure message clearly indicates what's missing
- [ ] Failure is due to missing functionality, not setup errors
- [ ] No false positives (test doesn't pass accidentally)

### Test Scope

- [ ] Test covers single behavior/requirement
- [ ] Test is independent of other tests
- [ ] Test does not rely on execution order
- [ ] Test sets up its own required state

### Naming Convention

```
# Function tests
test_<function>_<scenario>_<expected_result>

# Examples:
test_login_with_valid_credentials_returns_token
test_login_with_invalid_password_raises_auth_error
test_calculate_total_with_empty_cart_returns_zero
```

## GREEN Phase Checklist

Before moving to REFACTOR, verify:

### Implementation Quality

- [ ] All tests pass
- [ ] No new functionality beyond test requirements
- [ ] Implementation follows existing architecture patterns
- [ ] No obvious security vulnerabilities introduced

### Minimalism Verification

- [ ] Could remove any code and still pass tests? If yes, remove it
- [ ] No "just in case" error handling for untested scenarios
- [ ] No premature optimization
- [ ] No additional abstractions beyond what tests require

### Integration Check

- [ ] Implementation integrates with existing codebase
- [ ] No breaking changes to existing tests
- [ ] Dependencies are properly imported/injected
- [ ] Types/interfaces match existing patterns

## REFACTOR Phase Checklist

After each refactor step, verify:

### Test Stability

- [ ] All tests still pass
- [ ] No tests were modified during refactor
- [ ] Test coverage remains the same
- [ ] No new test failures introduced

### Code Quality Improvements

- [ ] Reduced code duplication (DRY)
- [ ] Improved naming clarity
- [ ] Simplified complex conditionals
- [ ] Extracted meaningful abstractions (if needed)

### Reversibility

- [ ] Change is small enough to easily revert
- [ ] Git commit made before refactor step
- [ ] Can explain what changed in one sentence

### When to Stop Refactoring

- Code is readable and self-documenting
- No obvious duplication remains
- Complexity is appropriate for requirements
- Further refactoring would be gold-plating

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

## Common Phase Violations

### Skipping RED

**Symptom:** Writing implementation before tests
**Problem:** Tests may be written to match implementation, not requirements
**Fix:** Delete implementation, write failing test first

### Incomplete GREEN

**Symptom:** Adding untested functionality
**Problem:** Untested code may have bugs, violates TDD principles
**Fix:** Remove untested code or add tests for it

### Premature REFACTOR

**Symptom:** Refactoring before all tests pass
**Problem:** Can't verify refactor didn't break anything
**Fix:** Get all tests passing first, then refactor

### Skipping REFACTOR

**Symptom:** Moving to next feature without cleaning up
**Problem:** Technical debt accumulates
**Fix:** Allocate time for refactoring in each cycle
