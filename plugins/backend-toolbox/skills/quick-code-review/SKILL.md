---
name: quick-code-review
description: This skill should be used when the user asks for a "quick review", "fast review", "quick code check", "hotfix review", "review this small change", "quick feedback", or needs a fast, time-constrained review focusing on 5 critical items security, correctness, test coverage, breaking changes, and error handling.
---

# Quick Code Review (5 Critical Items)

Fast, focused review for small changes, hotfixes, or time-constrained situations.

## When to Use Quick Review

- Small bug fixes (< 50 lines changed)
- Hotfixes that need to ship quickly
- Configuration changes
- Documentation-only updates
- Time-constrained reviews where deep analysis isn't feasible

## The 5 Critical Checks

### 1. Security

- No injection vulnerabilities (SQL, command, XSS)
- No secrets or credentials exposed
- No authentication/authorization bypasses
- No unsafe deserialization

### 2. Correctness

- Logic matches the stated requirements
- Edge cases handled (null, empty, boundaries)
- Error conditions produce appropriate behavior
- Changes don't break existing functionality

### 3. Test Coverage

- Critical paths have tests
- Tests assert meaningful behavior (not just "no exception")
- Tests are deterministic (no flakiness indicators)
- New behavior has corresponding test coverage

### 4. Breaking Changes

- API contracts preserved (function signatures, return types)
- Database schema changes are backward compatible
- Configuration changes have sensible defaults
- External integrations remain functional

### 5. Error Handling

- Errors are caught and handled appropriately
- Errors are logged with sufficient context
- User-facing errors are informative but not leaky
- Resource cleanup happens even on failure

## Quick Review Output Format

```markdown
## Quick Review Summary

**Verdict:** APPROVE / REQUEST_CHANGES / NEEDS_DISCUSSION

### Critical Issues (if any)

- [blocking issue 1]
- [blocking issue 2]

### Suggestions (non-blocking)

- [suggestion 1]
- [suggestion 2]

### Notes

- [any context or assumptions]
```

## When to Escalate to Deep Review

Switch to the **code-review-checklist** skill when you encounter:

- New features or significant refactors
- Security-sensitive code (auth, payments, PII handling)
- Performance-critical paths
- Public API changes
- Complex business logic
- Multi-service interactions
- Database migration scripts

### Related Skills

For comprehensive reviews, use the **code-review-checklist** skill which provides:

- Full architecture and design review
- Detailed readability assessment
- Complete test quality evaluation
- Performance and safety checks
