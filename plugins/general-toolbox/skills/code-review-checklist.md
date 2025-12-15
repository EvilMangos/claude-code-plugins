---
name: code-review-checklist
description: >
  Use when reviewing code changes, evaluating PRs, or checking code quality.
  Comprehensive checklist for code review covering architecture, readability, tests, and safety.
---

# Code Review Checklist

## 1. Architecture & Design

### Dependency Direction
- [ ] Dependencies flow inward (core doesn't depend on infrastructure)
- [ ] No circular dependencies between modules
- [ ] Clear module boundaries respected

### Abstraction Quality
- [ ] Interfaces are minimal and focused
- [ ] No leaky abstractions exposing implementation details
- [ ] Appropriate level of abstraction (not over/under-engineered)

### Single Responsibility
- [ ] Each function/method does one thing well
- [ ] Each module has a clear, focused purpose
- [ ] Changes are localized (not scattered across unrelated files)

## 2. Readability & Maintainability

### Naming
- [ ] Names describe intent, not implementation
- [ ] Consistent naming conventions with codebase
- [ ] No abbreviations unless universally understood

### Code Structure
- [ ] Functions are small and focused
- [ ] Control flow is straightforward (no deep nesting)
- [ ] Related code is grouped together

### Clarity
- [ ] No "clever" code when simple alternative exists
- [ ] Magic numbers/strings are named constants
- [ ] Complex logic has explanatory comments

## 3. Test Quality

### Coverage
- [ ] New behavior has corresponding tests
- [ ] Edge cases and error paths are tested
- [ ] Tests are in the correct location/file

### Test Design
- [ ] Tests verify observable behavior, not internals
- [ ] Assertions are specific and meaningful
- [ ] Test names describe the scenario and expectation

### Reliability
- [ ] Tests are deterministic (no flakiness)
- [ ] No dependencies on test execution order
- [ ] External dependencies are mocked appropriately

## 4. Performance & Safety

### Performance
- [ ] No obvious N+1 query patterns
- [ ] Hot paths avoid unnecessary allocations
- [ ] Data structures are appropriate for the access patterns

### Resource Management
- [ ] Resources are properly closed/cleaned up
- [ ] No memory leaks (event listeners, subscriptions)
- [ ] Timeouts are set for external calls

### Error Handling
- [ ] Errors are handled, not swallowed
- [ ] Error messages are useful for debugging
- [ ] Failure modes are graceful

### Security
- [ ] No injection vulnerabilities (SQL, XSS, command)
- [ ] Auth checks are present where needed
- [ ] Sensitive data is not logged/exposed

## Review Verdict Categories

### BLOCKING Issues
Must fix before merge:
- Architecture violations
- Security vulnerabilities
- Data integrity risks
- Missing critical tests
- Obvious bugs

### NON-BLOCKING Suggestions
Nice to fix but can merge:
- Style improvements
- Minor naming suggestions
- Performance micro-optimizations
- Additional test coverage

## Review Output Format

```markdown
## Summary
- [2-5 bullets describing the change and overall quality]

## Blocking Issues
1. [Issue description]
   - Why: [Explanation]
   - Fix: [Suggested resolution]

## Non-blocking Suggestions
- [Suggestion 1]
- [Suggestion 2]

## Test Feedback
- [Comments on test quality, coverage, design]
```
