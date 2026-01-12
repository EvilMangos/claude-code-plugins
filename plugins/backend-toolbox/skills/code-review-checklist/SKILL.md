---
name: code-review-checklist
description: This skill provides a structured code review framework with checklists for code quality. This skill should be used when the user asks to "review this code", "review my code", "do a code review", "check this PR", "evaluate PR", "review pull request", "check code quality", "review changes", "give feedback on code", "review this function", "is this code good", "audit this code", "analyze code quality", "check this code before merging", "review my pull request", or needs a comprehensive checklist for architecture and readability.
version: 0.1.0
---

# Code Review Checklist

Systematic approach to reviewing code changes for quality, correctness, and maintainability.

## Quick vs Deep Review

For time-constrained or small changes, use the **quick-code-review** skill.
Use the full checklist below for comprehensive reviews of new features or significant refactors.

## Review Workflow

1. **Understand context**: Read PR description, linked issues, and identify the change's purpose
2. **Scan for scope**: Review file list to understand change boundaries
3. **Evaluate architecture**: Check design decisions against established patterns
4. **Assess implementation**: Walk through code for readability, correctness, and edge cases
5. **Synthesize feedback**: List all issues that must be resolved before merge

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

## Review Verdict Categories

### Issues (All Must Be Resolved)

All issues must be fixed before merge:

- Architecture violations
- Data integrity risks
- Obvious bugs
- Style improvements
- Naming issues

## Review Output Format

```markdown
## Summary

- [2-5 bullets describing the change and overall quality]

## Issues

1. [Issue description]
    - Why: [Explanation]
    - Fix: [Suggested resolution]
```

## Additional Resources

### Reference Files

For detailed guidance, consult:

- **`references/review-patterns.md`** - When reviewing specific change types: strategies for bug fixes, feature additions, refactoring, and hotfixes with focused review questions for each
- **`references/security-checklist.md`** - When checking security: OWASP Top 10 mapped checklist covering input validation, authentication, authorization, injection prevention, and data protection

### Examples

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
