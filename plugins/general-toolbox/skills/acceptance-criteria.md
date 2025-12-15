---
name: acceptance-criteria
description: >
  Use when verifying implementation against requirements, checking feature completeness,
  or validating that changes satisfy the original request. Requirements validation and acceptance testing guide.
---

# Acceptance Criteria Guide

## Core Principle

**Implementation is complete when all requirements are met and verifiable.**

Every acceptance review must:
1. Extract requirements from the original request
2. Map each requirement to implementation
3. Verify behavior matches expectations
4. Identify gaps and risks

## Requirements Extraction

### Explicit Requirements
- Direct statements: "The system should..."
- Feature requests: "Add a button that..."
- Constraints: "Must work on mobile"

### Implicit Requirements
- Industry standards (accessibility, security)
- Consistency with existing behavior
- Error handling for obvious edge cases
- Performance expectations

### Ambiguous Areas
Flag for clarification:
- "Fast" - how fast?
- "User-friendly" - what does that mean?
- "Similar to X" - which aspects?

## Acceptance Checklist

### Functional Completeness
- [ ] All explicit requirements implemented
- [ ] Implicit requirements addressed
- [ ] Happy path works correctly
- [ ] Error paths handled gracefully

### Edge Cases
- [ ] Empty/null inputs
- [ ] Boundary values (min, max, zero)
- [ ] Invalid inputs
- [ ] Concurrent operations (if applicable)

### User Experience
- [ ] Flows are intuitive
- [ ] Feedback is clear (loading, success, error)
- [ ] Reversible actions have confirmation

### Integration
- [ ] Works with existing features
- [ ] No regression in related functionality
- [ ] Data consistency maintained

## Behavior Verification

### Test Coverage Assessment
| Requirement | Implementation | Test Coverage |
|-------------|----------------|---------------|
| [Requirement 1] | [File:line] | [Test name] |
| [Requirement 2] | [File:line] | [Missing] |

### Verification Methods
1. **Unit tests** - Individual function behavior
2. **Integration tests** - Component interaction
3. **Manual testing** - User flows
4. **Code inspection** - Logic correctness

## Gap Analysis

### Gap Categories

| Type | Severity | Action |
|------|----------|--------|
| Missing requirement | Critical | Must implement |
| Partial implementation | High | Complete before merge |
| No test coverage | Medium | Add tests |
| Assumption made | Low | Document and verify |

### Risk Assessment
For each gap, assess:
- **Impact**: What breaks if this isn't fixed?
- **Likelihood**: How often will this case occur?
- **Effort**: How hard is it to fix?

## Report Format

```markdown
## Acceptance Review Summary

**Verdict**: PASS / PARTIAL / FAIL

## Requirements Checklist
- [x] Requirement 1 - Implemented in file.ts:42
- [ ] Requirement 2 - Missing: [description]
- [~] Requirement 3 - Partial: [what's missing]

## Test Coverage
- Covered: [list]
- Missing: [list]

## Gaps & Risks
1. [Gap description]
   - Impact: [description]
   - Recommendation: [action]

## Assumptions Made
- [Assumption 1]: [basis for assumption]

## Open Questions
- [Question requiring clarification]
```
