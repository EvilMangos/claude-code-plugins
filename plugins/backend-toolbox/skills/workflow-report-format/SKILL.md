---
name: workflow-report-format
description: |
  This skill defines the standard format for workflow reports used in background agent orchestration.
  Use this skill when participating in a multi-agent workflow (develop-feature, fix-bug, etc.)
  where agents run sequentially in background and communicate via files.

  Key triggers: "workflow report", "write report to file", "background agent output",
  "orchestrator handoff", "file-based context", "workflow state".
version: 0.1.0
---

# Workflow Report Format

This skill standardizes how agents communicate in background-orchestrated workflows. Each agent:
1. Writes **full report** to a designated file
2. Returns **brief status** to the orchestrator

This keeps orchestrator context minimal while preserving full agent outputs for subsequent agents.

## Workflow State Directory

All workflow artifacts go in `.workflow/` at repository root:

```
.workflow/
├── metadata.json              # Workflow metadata (feature name, start time, current step)
├── 01-plan.md                 # plan-creator output
├── 02-tests-design.md         # automation-qa test design output
├── 03-tests-review.md         # tests-reviewer output
├── 04-implementation.md       # backend-developer output
├── 05-stabilization.md        # automation-qa stabilization output
├── 06-acceptance.md           # acceptance-reviewer output
├── 07-performance.md          # performance-specialist output
├── 08-security.md             # application-security-specialist output
├── 09-refactoring.md          # refactorer output
├── 10-code-review.md          # code-reviewer output
├── 11-documentation.md        # documentation-updater output
└── loop-iterations/           # For reflection loops
    ├── 07-performance-2.md    # Second iteration
    └── 08-security-2.md       # Second iteration
```

## Two-Part Output Pattern

Every agent in the workflow produces TWO outputs:

### Part 1: File Report (Full Details)

Written to `.workflow/{step}-{name}.md`. Contains everything the next agent needs.

### Part 2: Orchestrator Response (Brief Status)

Returned as agent response. Maximum 10 lines. Format:

```
STATUS: PASS | PARTIAL | FAIL | DONE
FILE: .workflow/{step}-{name}.md
SUMMARY: One sentence describing outcome
NEXT_INPUT: List of files the next agent should read
---
[Optional: 2-5 bullet key points]
```

## Standard File Report Structure

Every file report follows this structure:

```markdown
# {Step Name} Report

**Status:** PASS | PARTIAL | FAIL | DONE
**Agent:** {agent-name}
**Timestamp:** {ISO timestamp}
**Input Files:** {list of files this agent read}

## Summary
2-5 bullets summarizing the work done or findings.

## {Agent-Specific Sections}
See agent-specific templates below.

## Handoff Notes
- What the next agent needs to know
- Any assumptions made
- Open questions or concerns

## Files Modified
- `path/to/file.ts` - description of change
```

---

## Agent-Specific Templates

### plan-creator → `.workflow/01-plan.md`

```markdown
# Planning Report

**Status:** DONE
**Agent:** plan-creator
**Timestamp:** {ISO}
**Input Files:** user request, relevant source files

## Summary
- Brief description of the feature
- Key architectural decisions
- Scope boundaries

## Requirements
1. REQ-1: {requirement description}
2. REQ-2: {requirement description}
...

## Implementation Plan

### Test Steps (for automation-qa)
1. {test step with file location}
2. {test step}

### Implementation Steps (for backend-developer)
1. {implementation step with file location}
2. {implementation step}

## Affected Files
- `src/path/file.ts` - {what changes}

## Risks & Open Questions
- {risk or question}

## Handoff Notes
- automation-qa should start with Test Steps
- Key patterns to follow: {patterns}
```

**Orchestrator Response:**
```
STATUS: DONE
FILE: .workflow/01-plan.md
SUMMARY: Created implementation plan with {N} requirements and {M} steps
NEXT_INPUT: .workflow/01-plan.md
---
- {N} requirements identified
- {M} implementation steps planned
- Key risk: {main risk}
```

---

### automation-qa (Test Design) → `.workflow/02-tests-design.md`

```markdown
# Test Design Report

**Status:** DONE
**Agent:** automation-qa
**Timestamp:** {ISO}
**Input Files:** .workflow/01-plan.md

## Summary
- Tests designed for {N} requirements
- {M} test files created/modified

## Requirements Coverage

| Requirement | Test File | Test Name | Coverage |
|-------------|-----------|-----------|----------|
| REQ-1 | `tests/foo.test.ts` | `should do X` | Full |
| REQ-2 | `tests/bar.test.ts` | `should handle Y` | Partial |

## Test Files Modified
- `tests/foo.test.ts` - added {N} tests
- `tests/bar.test.ts` - added {M} tests

## RED Stage Verification
```bash
# Run these commands to verify tests fail (RED)
/run-tests tests/foo.test.ts
/run-tests tests/bar.test.ts
```

### Expected Failures
- `should do X` - fails because {reason}
- `should handle Y` - fails because {reason}

## Handoff Notes
- tests-reviewer should verify coverage completeness
- Edge cases covered: {list}
- Edge cases NOT covered (intentional): {list}
```

**Orchestrator Response:**
```
STATUS: DONE
FILE: .workflow/02-tests-design.md
SUMMARY: Designed {N} tests covering {M} requirements, verified RED stage
NEXT_INPUT: .workflow/01-plan.md, .workflow/02-tests-design.md
---
- {N} tests created in {M} files
- All tests fail as expected (RED confirmed)
- Run command: /run-tests {pattern}
```

---

### tests-reviewer → `.workflow/03-tests-review.md`

```markdown
# Test Review Report

**Status:** PASS | PARTIAL | FAIL
**Agent:** tests-reviewer
**Timestamp:** {ISO}
**Input Files:** .workflow/01-plan.md, .workflow/02-tests-design.md

## Summary
- Verdict: {PASS|PARTIAL|FAIL}
- {N} requirements fully covered
- {M} issues found

## Requirements Coverage Checklist

| Requirement | Status | Notes |
|-------------|--------|-------|
| REQ-1 | ✅ | Fully covered |
| REQ-2 | ⚠️ | Missing edge case |
| REQ-3 | ❌ | No test coverage |

## Blocking Issues
1. **{Issue Title}**
   - Location: `tests/file.test.ts:42`
   - Problem: {description}
   - Impact: {why this matters}
   - Fix: {suggested resolution}

## Non-Blocking Improvements
- {suggestion}

## Flake Risk Assessment
- Low/Medium/High
- {reasoning}

## Handoff Notes
- If PASS: backend-developer can proceed with implementation
- If PARTIAL/FAIL: automation-qa must address blocking issues first
```

**Orchestrator Response:**
```
STATUS: PASS | PARTIAL | FAIL
FILE: .workflow/03-tests-review.md
SUMMARY: {PASS: Tests approved | PARTIAL/FAIL: {N} blocking issues found}
NEXT_INPUT: .workflow/01-plan.md, .workflow/02-tests-design.md, .workflow/03-tests-review.md
---
- {N}/{M} requirements covered
- Blocking issues: {count or "none"}
- Verdict: {verdict with brief reason}
```

---

### backend-developer → `.workflow/04-implementation.md`

```markdown
# Implementation Report

**Status:** DONE
**Agent:** backend-developer
**Timestamp:** {ISO}
**Input Files:** .workflow/01-plan.md, .workflow/02-tests-design.md

## Summary
- Implemented {N} requirements
- {M} files modified
- All targeted tests now pass (GREEN)

## Implementation Log

### Step 1: {description}
- Files: `src/file.ts`
- Changes: {what changed}
- Test run: `/run-tests tests/specific.test.ts` → PASS

### Step 2: {description}
- Files: `src/other.ts`
- Changes: {what changed}
- Test run: `/run-tests tests/specific.test.ts` → PASS

## Files Modified
- `src/file.ts` - {summary of changes}
- `src/other.ts` - {summary of changes}

## Test Results
```
/run-tests {pattern}
✓ {N} tests passed
```

## Handoff Notes
- Ready for stabilization (broader test run)
- Potential performance concern: {if any}
- Potential security concern: {if any}
```

**Orchestrator Response:**
```
STATUS: DONE
FILE: .workflow/04-implementation.md
SUMMARY: Implemented feature in {N} steps, all {M} tests pass (GREEN)
NEXT_INPUT: .workflow/01-plan.md, .workflow/04-implementation.md
---
- {N} files modified
- {M} tests passing
- Ready for stabilization
```

---

### automation-qa (Stabilization) → `.workflow/05-stabilization.md`

```markdown
# Stabilization Report

**Status:** PASS | PARTIAL | FAIL
**Agent:** automation-qa
**Timestamp:** {ISO}
**Input Files:** .workflow/01-plan.md, .workflow/04-implementation.md

## Summary
- Verdict: {PASS|PARTIAL|FAIL}
- Broader test scope: {description}
- Additional tests needed: {YES|NO}

## Broader Test Run
```bash
/run-tests {broader-pattern}
```

### Results
- Total: {N} tests
- Passed: {M}
- Failed: {K}

### Failures (if any)
1. `test name` - {failure reason}

## Additional Tests Needed
- YES/NO
- {If YES: description of what's missing}

## Regression Risk Assessment
- Low/Medium/High
- {reasoning}

## Handoff Notes
- If PASS: Ready for acceptance review
- If PARTIAL/FAIL: Issues need TDD loop resolution
```

**Orchestrator Response:**
```
STATUS: PASS | PARTIAL | FAIL
FILE: .workflow/05-stabilization.md
SUMMARY: {PASS: Stabilization complete | PARTIAL/FAIL: {N} issues found}
NEXT_INPUT: .workflow/01-plan.md, .workflow/04-implementation.md, .workflow/05-stabilization.md
---
- Broader test run: {N} passed, {M} failed
- Additional tests needed: {YES|NO}
- Verdict: {verdict}
```

---

### acceptance-reviewer → `.workflow/06-acceptance.md`

```markdown
# Acceptance Review Report

**Status:** PASS | PARTIAL | FAIL
**Agent:** acceptance-reviewer
**Timestamp:** {ISO}
**Input Files:** .workflow/01-plan.md, .workflow/04-implementation.md, .workflow/05-stabilization.md

## Summary
- Verdict: {PASS|PARTIAL|FAIL}
- {N}/{M} requirements met

## Requirements Checklist

| ID | Requirement | Status | Evidence |
|----|-------------|--------|----------|
| REQ-1 | {description} | ✅ | `src/file.ts:42` |
| REQ-2 | {description} | ⚠️ | Partial implementation |
| REQ-3 | {description} | ❌ | Not implemented |

## Functional Gaps (if any)
1. **{Gap Title}**
   - Requirement: REQ-{N}
   - Expected: {what should happen}
   - Actual: {what happens}
   - Severity: BLOCKING | NON-BLOCKING

## Handoff Notes
- If PASS: Ready for performance check
- If PARTIAL/FAIL: TDD loop needed for gaps
```

**Orchestrator Response:**
```
STATUS: PASS | PARTIAL | FAIL
FILE: .workflow/06-acceptance.md
SUMMARY: {PASS: All requirements met | PARTIAL/FAIL: {N} gaps found}
NEXT_INPUT: .workflow/01-plan.md, .workflow/04-implementation.md, .workflow/06-acceptance.md
---
- Requirements: {N}/{M} met
- Blocking gaps: {count or "none"}
- Verdict: {verdict}
```

---

### performance-specialist → `.workflow/07-performance.md`

```markdown
# Performance Review Report

**Status:** PASS | PARTIAL | FAIL
**Agent:** performance-specialist
**Timestamp:** {ISO}
**Input Files:** .workflow/04-implementation.md

## Summary
- Verdict: {PASS|PARTIAL|FAIL}
- {N} findings ({M} blocking)

## Findings

### Blocking Issues
1. **{Issue Title}**
   - Location: `src/file.ts:42`
   - Category: {Algorithm|Database|Memory|I/O|Caching|Concurrency}
   - Problem: {description}
   - Impact: {performance impact}
   - Fix: {recommended solution}

### Non-Blocking Optimizations
1. **{Optimization Title}**
   - Location: `src/file.ts:100`
   - Benefit: {expected improvement}
   - Suggestion: {how to optimize}

## Handoff Notes
- If PASS: Ready for security check
- If PARTIAL/FAIL: backend-developer must fix blocking issues
```

**Orchestrator Response:**
```
STATUS: PASS | PARTIAL | FAIL
FILE: .workflow/07-performance.md
SUMMARY: {PASS: No blocking issues | PARTIAL/FAIL: {N} blocking issues}
NEXT_INPUT: .workflow/04-implementation.md, .workflow/07-performance.md
---
- Blocking: {count}
- Non-blocking: {count}
- Verdict: {verdict}
```

---

### application-security-specialist → `.workflow/08-security.md`

```markdown
# Security Review Report

**Status:** PASS | PARTIAL | FAIL
**Agent:** application-security-specialist
**Timestamp:** {ISO}
**Input Files:** .workflow/04-implementation.md

## Summary
- Verdict: {PASS|PARTIAL|FAIL}
- {N} findings ({M} blocking)

## Findings

### Blocking Vulnerabilities
1. **{Vulnerability Title}**
   - Location: `src/file.ts:42`
   - Category: {Injection|Auth|XSS|CSRF|Exposure|etc}
   - Severity: Critical | High | Medium
   - Problem: {description}
   - Risk: {potential exploit}
   - Fix: {recommended remediation}

### Non-Blocking Hardening
1. **{Recommendation Title}**
   - Location: `src/file.ts:100`
   - Category: {category}
   - Suggestion: {hardening recommendation}

## OWASP Top 10 Checklist
- [ ] A01: Broken Access Control
- [ ] A02: Cryptographic Failures
- [ ] A03: Injection
...

## Handoff Notes
- If PASS: Ready for refactoring
- If PARTIAL/FAIL: backend-developer must fix blocking vulnerabilities
```

**Orchestrator Response:**
```
STATUS: PASS | PARTIAL | FAIL
FILE: .workflow/08-security.md
SUMMARY: {PASS: No vulnerabilities | PARTIAL/FAIL: {N} blocking vulnerabilities}
NEXT_INPUT: .workflow/04-implementation.md, .workflow/08-security.md
---
- Blocking: {count}
- Non-blocking: {count}
- Verdict: {verdict}
```

---

### refactorer → `.workflow/09-refactoring.md`

```markdown
# Refactoring Report

**Status:** DONE
**Agent:** refactorer
**Timestamp:** {ISO}
**Input Files:** .workflow/04-implementation.md

## Summary
- {N} refactoring steps completed
- All tests still pass

## Refactoring Log

### Step 1: {description}
- Type: {Extract|Rename|Move|Simplify|etc}
- Files: `src/file.ts`
- Before: {brief description}
- After: {brief description}
- Test run: `/run-tests {pattern}` → PASS

### Step 2: {description}
...

## Files Modified
- `src/file.ts` - {changes}

## Follow-up Tasks (larger refactors for later)
- {description of deferred refactoring}

## Handoff Notes
- Ready for code review
- Code quality improvements: {summary}
```

**Orchestrator Response:**
```
STATUS: DONE
FILE: .workflow/09-refactoring.md
SUMMARY: Completed {N} refactoring steps, all tests pass
NEXT_INPUT: .workflow/04-implementation.md, .workflow/09-refactoring.md
---
- {N} refactoring steps
- {M} files modified
- All tests passing
```

---

### code-reviewer → `.workflow/10-code-review.md`

```markdown
# Code Review Report

**Status:** PASS | PARTIAL | FAIL
**Agent:** code-reviewer
**Timestamp:** {ISO}
**Input Files:** .workflow/04-implementation.md, .workflow/09-refactoring.md

## Summary
- Verdict: {PASS|PARTIAL|FAIL}
- {N} findings ({M} blocking)

## Blocking Issues
1. **{Issue Title}**
   - Location: `src/file.ts:42`
   - Category: {Architecture|Maintainability|Style|Tests}
   - Problem: {description}
   - Fix: {suggested resolution}
   - Route to: {automation-qa + backend-developer | refactorer}

## Non-Blocking Suggestions
- {suggestion}

## Positive Observations
- {good practice observed}

## Handoff Notes
- If PASS: Ready for documentation
- If PARTIAL/FAIL: Route issues to appropriate agents
```

**Orchestrator Response:**
```
STATUS: PASS | PARTIAL | FAIL
FILE: .workflow/10-code-review.md
SUMMARY: {PASS: Approved | PARTIAL/FAIL: {N} blocking issues}
NEXT_INPUT: .workflow/10-code-review.md
---
- Blocking: {count}
- Non-blocking: {count}
- Verdict: {verdict}
```

---

### documentation-updater → `.workflow/11-documentation.md`

```markdown
# Documentation Update Report

**Status:** DONE
**Agent:** documentation-updater
**Timestamp:** {ISO}
**Input Files:** .workflow/01-plan.md, .workflow/04-implementation.md

## Summary
- {N} documentation files updated

## Updates Made

### {file path}
- Section: {section name}
- Change: {what was updated}

## Files Modified
- `README.md` - {changes}
- `docs/api.md` - {changes}

## Handoff Notes
- Documentation is now consistent with implementation
- No code changes made
```

**Orchestrator Response:**
```
STATUS: DONE
FILE: .workflow/11-documentation.md
SUMMARY: Updated {N} documentation files
NEXT_INPUT: .workflow/11-documentation.md
---
- {N} files updated
- {list of files}
```

---

## Loop Iteration Naming

When reflection loops occur, use incremented filenames:

```
.workflow/07-performance.md      # First review
.workflow/loop-iterations/07-performance-2.md  # After first fix
.workflow/loop-iterations/07-performance-3.md  # After second fix
```

The orchestrator tracks which iteration is current.

---

## Orchestrator Decision Logic

The orchestrator uses STATUS to decide next action:

| Status | Orchestrator Action |
|--------|---------------------|
| DONE | Proceed to next step |
| PASS | Proceed to next step |
| PARTIAL | Enter fix loop (may proceed with warnings) |
| FAIL | Enter fix loop (must fix before proceeding) |

For PARTIAL/FAIL in review steps:
1. Route to appropriate fixer agent (automation-qa, backend-developer, refactorer)
2. Fixer reads the review report file
3. Fixer produces fix report
4. Re-run reviewer
5. Repeat until PASS

---

## Related Skills

- `code-review-checklist` - Detailed review criteria
- `design-assessment` - Design quality evaluation
- `acceptance-criteria` - Requirements verification
- `tdd-workflow` - Test-driven development process
