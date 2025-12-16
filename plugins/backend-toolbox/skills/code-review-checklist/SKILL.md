---
name: code-review-checklist
description: >
  This skill should be used when the user asks to "review code", "review my code",
  "evaluate PR", "check code quality", "review changes", "give feedback on code",
  "code review", "review this function", "is this code good", or needs a comprehensive
  checklist for architecture, readability, tests, and safety.
---

# Code Review Checklist

Systematic approach to reviewing code changes for quality, correctness, and maintainability.

## Quick vs Deep Review

For time-constrained or small changes, use the **quick-code-review** skill (5 critical items).
Use the full checklist below for comprehensive reviews of new features, security-sensitive code, or significant
refactors.

## Review Workflow

1. **Understand context**: Read PR description, linked issues, and identify the change's purpose
2. **Scan for scope**: Review file list to understand change boundaries
3. **Evaluate architecture**: Check design decisions against established patterns
4. **Assess implementation**: Walk through code for readability, correctness, and edge cases
5. **Verify testing**: Ensure adequate coverage and test quality
6. **Check safety**: Look for security, performance, and resource concerns
7. **Synthesize feedback**: Categorize issues as blocking vs. non-blocking

## Quick Checklist

### Architecture & Design

#### Dependency Direction

- [ ] Dependencies flow inward (core doesn't depend on infrastructure)
- [ ] No circular dependencies between modules
- [ ] Clear module boundaries respected

#### Abstraction Quality

- [ ] Interfaces are minimal and focused
- [ ] No leaky abstractions exposing implementation details
- [ ] Appropriate level of abstraction (not over/under-engineered)

#### Single Responsibility

- [ ] Each function/method does one thing well
- [ ] Each module has a clear, focused purpose
- [ ] Changes are localized (not scattered across unrelated files)

### Readability & Maintainability

#### Naming

- [ ] Names describe intent, not implementation
- [ ] Consistent naming conventions with codebase
- [ ] No abbreviations unless universally understood

#### Code Structure

- [ ] Functions are small and focused
- [ ] Control flow is straightforward (no deep nesting)
- [ ] Related code is grouped together

#### Clarity

- [ ] No "clever" code when simple alternative exists
- [ ] Magic numbers/strings are named constants
- [ ] Complex logic has explanatory comments

### Test Quality

#### Coverage

- [ ] New behavior has corresponding tests
- [ ] Edge cases and error paths are tested
- [ ] Tests are in the correct location/file

#### Test Design

- [ ] Tests verify observable behavior, not internals
- [ ] Assertions are specific and meaningful
- [ ] Test names describe the scenario and expectation

#### Reliability

- [ ] Tests are deterministic (no flakiness)
- [ ] No dependencies on test execution order
- [ ] External dependencies are mocked appropriately

### Performance & Safety

#### Performance

- [ ] No obvious N+1 query patterns
- [ ] Hot paths avoid unnecessary allocations
- [ ] Data structures are appropriate for the access patterns

#### Resource Management

- [ ] Resources are properly closed/cleaned up
- [ ] No memory leaks (event listeners, subscriptions)
- [ ] Timeouts are set for external calls

#### Error Handling

- [ ] Errors are handled, not swallowed
- [ ] Error messages are useful for debugging
- [ ] Failure modes are graceful

#### Security

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

## Additional Resources

For detailed guidance and examples, consult:

- **`references/review-patterns.md`** - Common review scenarios and how to handle them
- **`references/security-checklist.md`** - Detailed security review guidance
- **`examples/sample-review.md`** - Complete example of a well-structured code review

### Related Skills

For time-constrained reviews, use the **quick-code-review** skill for:

- Fast 5-item checklist for small changes
- Hotfix and configuration review
- When to escalate to full review

When evaluating architecture and design quality, consult the **software-design-principles** skill for:

- SOLID principles to assess design adherence
- Design patterns to identify appropriate solutions
- Coupling/cohesion analysis for architectural review
- Dependency injection evaluation
