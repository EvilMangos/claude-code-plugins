---
name: workflow-report-format
description: This skill defines the standard format for workflow reports used in background agent orchestration. Use this skill when participating in a multi-agent workflow (develop-feature, fix-bug, etc.) where agents run sequentially in background and communicate via files. Key triggers - "workflow report", "write report to file", "background agent output", "orchestrator handoff", "file-based context", "workflow state".
version: 0.1.0
---

# Workflow Report Format

This skill standardizes how agents communicate in background-orchestrated workflows. Each agent:
1. Writes **full report** to a designated file (`{name}.md`)
2. Writes **brief status** to a signal file (`{name}-report.md`)

The orchestrator polls for the signal file and reads only the brief status. This keeps orchestrator context minimal while preserving full agent outputs for subsequent agents.

## Multi-Instance Support

Multiple Claude Code instances can run workflows concurrently in the same repository. Each workflow gets its own isolated subdirectory.

### Task ID Generation

When a workflow starts, the orchestrator generates a unique task ID:

```
{command}-{slug}-{timestamp}
```

Components:
- `command`: The workflow command name (`develop-feature`, `fix-bug`, etc.)
- `slug`: URL-safe version of feature/task description (lowercase, hyphens, max 30 chars)
- `timestamp`: Unix timestamp (seconds)

Examples:
- `develop-feature-user-auth-1702834567`
- `fix-bug-login-timeout-1702834890`
- `refactor-payment-module-1702835012`

### Workflow Directory Structure

Each workflow creates its own subdirectory under `.workflow/`:

```
.workflow/
├── develop-feature-user-auth-1702834567/
│   ├── metadata.json
│   ├── requirements.md
│   ├── plan.md
│   └── tests-design.md
├── fix-bug-login-timeout-1702834890/
│   ├── metadata.json
│   ├── requirements.md
│   └── ...
└── .gitignore                  # Should contain: *
```

### WORKFLOW_DIR Variable

The orchestrator passes the full workflow directory path to every agent:

```
WORKFLOW_DIR: .workflow/{task-id}
```

**All file paths are relative to WORKFLOW_DIR.** When agents see instructions like:
- "Write to: `{WORKFLOW_DIR}/implementation.md`"
- "Read: `{WORKFLOW_DIR}/plan.md`"

They use the actual path like:
- `.workflow/develop-feature-user-auth-1702834567/implementation.md`

### Agent Prompt Requirements

Every agent prompt MUST include:

```
## Workflow Directory
WORKFLOW_DIR: .workflow/{task-id}

All file operations use this directory:
- Read from: {WORKFLOW_DIR}/*.md
- Write to: {WORKFLOW_DIR}/{name}.md
```

### File Report Paths

Within a workflow, each step produces two files:
- **Full report:** `{name}.md` - detailed output for next agents
- **Signal file:** `{name}-report.md` - brief status for orchestrator

```
{WORKFLOW_DIR}/
├── metadata.json                  # Workflow metadata (feature name, start time, current step)
├── requirements.md                # Full report: initial requirements
├── requirements-report.md         # Signal: requirements status
├── plan.md                        # Full report: plan-creator output
├── plan-report.md                 # Signal: plan status
├── tests-design.md                # Full report: automation-qa test design
├── tests-design-report.md         # Signal: tests-design status
├── tests-review.md                # Full report: tests-reviewer output
├── tests-review-report.md         # Signal: tests-review status
├── implementation.md              # Full report: backend-developer output
├── implementation-report.md       # Signal: implementation status
├── stabilization.md               # Full report: automation-qa stabilization
├── stabilization-report.md        # Signal: stabilization status
├── acceptance.md                  # Full report: acceptance-reviewer output
├── acceptance-report.md           # Signal: acceptance status
├── performance.md                 # Full report: performance-specialist output
├── performance-report.md          # Signal: performance status
├── security.md                    # Full report: security-specialist output
├── security-report.md             # Signal: security status
├── refactoring.md                 # Full report: refactorer output
├── refactoring-report.md          # Signal: refactoring status
├── code-review.md                 # Full report: code-reviewer output
├── code-review-report.md          # Signal: code-review status
├── documentation.md               # Full report: documentation-updater output
└── documentation-report.md        # Signal: documentation status
```

## Two-Part Output Pattern

Every agent in the workflow produces TWO files:

### Part 1: Full Report (`{name}.md`)

Written to `{WORKFLOW_DIR}/{name}.md`. Contains everything the next agent needs.

### Part 2: Signal File (`{name}-report.md`)

Written to `{WORKFLOW_DIR}/{name}-report.md`. Brief status for the orchestrator. Maximum 10 lines. Format:

```
STATUS: PASS | PARTIAL | FAIL | DONE | ERROR
FILE: {WORKFLOW_DIR}/{name}.md
SUMMARY: One sentence describing outcome
NEXT_INPUT: List of files the next agent should read
---
[Optional: 2-5 bullet key points]
```

**Important:** The orchestrator polls for this signal file using:
```bash
${CLAUDE_PLUGIN_ROOT}/scripts/wait-for-report.sh {WORKFLOW_DIR}/{name}-report.md
```

The script polls every 10 seconds until the file appears. Stale files are not an issue because each workflow run uses a unique TASK_ID directory.

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

### plan-creator → `plan.md`

```markdown
# Planning Report

**Status:** DONE
**Agent:** plan-creator
**Timestamp:** {ISO}
**Input Files:** {as specified in orchestrator prompt}

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

**Signal File (`plan-report.md`):**
```
STATUS: DONE
FILE: {WORKFLOW_DIR}/plan.md
SUMMARY: Created implementation plan with {N} requirements and {M} steps
NEXT_INPUT: {WORKFLOW_DIR}/plan.md
---
- {N} requirements identified
- {M} implementation steps planned
- Key risk: {main risk}
```

---

### automation-qa (Test Design) → `tests-design.md`

```markdown
# Test Design Report

**Status:** DONE
**Agent:** automation-qa
**Timestamp:** {ISO}
**Input Files:** {as specified in orchestrator prompt}

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

**Signal File (`tests-design-report.md`):**
```
STATUS: DONE
FILE: {WORKFLOW_DIR}/tests-design.md
SUMMARY: Designed {N} tests covering {M} requirements, verified RED stage
NEXT_INPUT: {WORKFLOW_DIR}/plan.md, {WORKFLOW_DIR}/tests-design.md
---
- {N} tests created in {M} files
- All tests fail as expected (RED confirmed)
- Run command: /run-tests {pattern}
```

---

### tests-reviewer → `tests-review.md`

```markdown
# Test Review Report

**Status:** PASS | PARTIAL | FAIL
**Agent:** tests-reviewer
**Timestamp:** {ISO}
**Input Files:** {as specified in orchestrator prompt}

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

**Signal File (`tests-review-report.md`):**
```
STATUS: PASS | PARTIAL | FAIL
FILE: {WORKFLOW_DIR}/tests-review.md
SUMMARY: {PASS: Tests approved | PARTIAL/FAIL: {N} blocking issues found}
NEXT_INPUT: {WORKFLOW_DIR}/plan.md, {WORKFLOW_DIR}/tests-design.md, {WORKFLOW_DIR}/tests-review.md
---
- {N}/{M} requirements covered
- Blocking issues: {count or "none"}
- Verdict: {verdict with brief reason}
```

---

### backend-developer → `implementation.md`

```markdown
# Implementation Report

**Status:** DONE
**Agent:** backend-developer
**Timestamp:** {ISO}
**Input Files:** {as specified in orchestrator prompt}

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

**Signal File (`implementation-report.md`):**
```
STATUS: DONE
FILE: {WORKFLOW_DIR}/implementation.md
SUMMARY: Implemented feature in {N} steps, all {M} tests pass (GREEN)
NEXT_INPUT: {WORKFLOW_DIR}/plan.md, {WORKFLOW_DIR}/implementation.md
---
- {N} files modified
- {M} tests passing
- Ready for stabilization
```

---

### automation-qa (Stabilization) → `stabilization.md`

```markdown
# Stabilization Report

**Status:** PASS | PARTIAL | FAIL
**Agent:** automation-qa
**Timestamp:** {ISO}
**Input Files:** {as specified in orchestrator prompt}

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

**Signal File (`stabilization-report.md`):**
```
STATUS: PASS | PARTIAL | FAIL
FILE: {WORKFLOW_DIR}/stabilization.md
SUMMARY: {PASS: Stabilization complete | PARTIAL/FAIL: {N} issues found}
NEXT_INPUT: {WORKFLOW_DIR}/plan.md, {WORKFLOW_DIR}/implementation.md, {WORKFLOW_DIR}/stabilization.md
---
- Broader test run: {N} passed, {M} failed
- Additional tests needed: {YES|NO}
- Verdict: {verdict}
```

---

### acceptance-reviewer → `acceptance.md`

```markdown
# Acceptance Review Report

**Status:** PASS | PARTIAL | FAIL
**Agent:** acceptance-reviewer
**Timestamp:** {ISO}
**Input Files:** {as specified in orchestrator prompt}

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

**Signal File (`acceptance-report.md`):**
```
STATUS: PASS | PARTIAL | FAIL
FILE: {WORKFLOW_DIR}/acceptance.md
SUMMARY: {PASS: All requirements met | PARTIAL/FAIL: {N} gaps found}
NEXT_INPUT: {WORKFLOW_DIR}/plan.md, {WORKFLOW_DIR}/implementation.md, {WORKFLOW_DIR}/acceptance.md
---
- Requirements: {N}/{M} met
- Blocking gaps: {count or "none"}
- Verdict: {verdict}
```

---

### performance-specialist → `performance.md`

```markdown
# Performance Review Report

**Status:** PASS | PARTIAL | FAIL
**Agent:** performance-specialist
**Timestamp:** {ISO}
**Input Files:** {as specified in orchestrator prompt}

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

**Signal File (`performance-report.md`):**
```
STATUS: PASS | PARTIAL | FAIL
FILE: {WORKFLOW_DIR}/performance.md
SUMMARY: {PASS: No blocking issues | PARTIAL/FAIL: {N} blocking issues}
NEXT_INPUT: {WORKFLOW_DIR}/implementation.md, {WORKFLOW_DIR}/performance.md
---
- Blocking: {count}
- Non-blocking: {count}
- Verdict: {verdict}
```

---

### application-security-specialist → `security.md`

```markdown
# Security Review Report

**Status:** PASS | PARTIAL | FAIL
**Agent:** application-security-specialist
**Timestamp:** {ISO}
**Input Files:** {as specified in orchestrator prompt}

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

**Signal File (`security-report.md`):**
```
STATUS: PASS | PARTIAL | FAIL
FILE: {WORKFLOW_DIR}/security.md
SUMMARY: {PASS: No vulnerabilities | PARTIAL/FAIL: {N} blocking vulnerabilities}
NEXT_INPUT: {WORKFLOW_DIR}/implementation.md, {WORKFLOW_DIR}/security.md
---
- Blocking: {count}
- Non-blocking: {count}
- Verdict: {verdict}
```

---

### refactorer → `refactoring.md`

```markdown
# Refactoring Report

**Status:** DONE
**Agent:** refactorer
**Timestamp:** {ISO}
**Input Files:** {as specified in orchestrator prompt}

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

**Signal File (`refactoring-report.md`):**
```
STATUS: DONE
FILE: {WORKFLOW_DIR}/refactoring.md
SUMMARY: Completed {N} refactoring steps, all tests pass
NEXT_INPUT: {WORKFLOW_DIR}/implementation.md, {WORKFLOW_DIR}/refactoring.md
---
- {N} refactoring steps
- {M} files modified
- All tests passing
```

---

### code-reviewer → `code-review.md`

```markdown
# Code Review Report

**Status:** PASS | PARTIAL | FAIL
**Agent:** code-reviewer
**Timestamp:** {ISO}
**Input Files:** {as specified in orchestrator prompt}

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

**Signal File (`code-review-report.md`):**
```
STATUS: PASS | PARTIAL | FAIL
FILE: {WORKFLOW_DIR}/code-review.md
SUMMARY: {PASS: Approved | PARTIAL/FAIL: {N} blocking issues}
NEXT_INPUT: {WORKFLOW_DIR}/code-review.md
---
- Blocking: {count}
- Non-blocking: {count}
- Verdict: {verdict}
```

---

### documentation-updater → `documentation.md`

```markdown
# Documentation Update Report

**Status:** DONE
**Agent:** documentation-updater
**Timestamp:** {ISO}
**Input Files:** {as specified in orchestrator prompt}

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

**Signal File (`documentation-report.md`):**
```
STATUS: DONE
FILE: {WORKFLOW_DIR}/documentation.md
SUMMARY: Updated {N} documentation files
NEXT_INPUT: {WORKFLOW_DIR}/documentation.md
---
- {N} files updated
- {list of files}
```

---

## Reflection Loops

Reflection loops occur when a reviewer returns PARTIAL or FAIL and issues must be fixed before proceeding.

### Loop Flow (File Overwriting)

Reports are **overwritten** on each iteration - we care about the final passing state, not the history.

```
┌─────────────────────────────────────────────────────────────────────┐
│  REVIEWER (e.g., performance-specialist)                            │
│  - Reads: {WORKFLOW_DIR}/implementation.md                          │
│  - Writes: {WORKFLOW_DIR}/performance.md                            │
│  - Returns: STATUS: FAIL, BLOCKING issues: 2                        │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼ (FAIL → loop)
┌─────────────────────────────────────────────────────────────────────┐
│  FIXER (e.g., backend-developer)                                    │
│  - Reads: {WORKFLOW_DIR}/performance.md (the findings)              │
│  - Fixes BLOCKING issues in code                                    │
│  - Overwrites: {WORKFLOW_DIR}/implementation.md                     │
│  - Returns: STATUS: DONE                                            │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  REVIEWER (re-run)                                                  │
│  - Reads: {WORKFLOW_DIR}/implementation.md (updated)                │
│  - Overwrites: {WORKFLOW_DIR}/performance.md                        │
│  - Returns: STATUS: PASS (or FAIL → continue loop)                  │
└─────────────────────────────────────────────────────────────────────┘
```

### File Paths (Overwrite Pattern)

All iterations use the same file paths:

```
{WORKFLOW_DIR}/
├── implementation.md    # Updated by fixer on each iteration
├── implementation-report.md
├── performance.md       # Overwritten by reviewer on each iteration
└── performance-report.md
```

Benefits:
- Simpler orchestrator logic (no iteration tracking)
- Agents always read/write predictable paths
- Final state is what matters

### Orchestrator Responsibilities in Loops

The orchestrator MUST:

1. **Pass WORKFLOW_DIR** - The full path to this workflow's directory
2. **Specify files to read** - Previous findings
3. **Specify task** - What BLOCKING issues to address
4. **Track iteration count internally** (for max iteration limit)

Example orchestrator prompt for fixer:
```
## Workflow Directory
WORKFLOW_DIR: .workflow/develop-feature-user-auth-1702834567

## Task
Fix the BLOCKING performance issues identified in the review.

## Input Files
Read: {WORKFLOW_DIR}/performance.md

## Focus On
Address ONLY the BLOCKING issues listed. Do not address NON-BLOCKING.

## Output
1. Write FULL report to: {WORKFLOW_DIR}/implementation.md (overwrite)
2. Write SHORT status to: {WORKFLOW_DIR}/implementation-report.md
```

Example orchestrator prompt for re-review:
```
## Workflow Directory
WORKFLOW_DIR: .workflow/develop-feature-user-auth-1702834567

## Task
Re-review performance after fixes were applied.

## Input Files
Read:
- {WORKFLOW_DIR}/implementation.md (updated with fixes)

## Output
1. Write FULL report to: {WORKFLOW_DIR}/performance.md (overwrite)
2. Write SHORT status to: {WORKFLOW_DIR}/performance-report.md
```

### Loop Termination

The orchestrator exits the loop when:
1. Reviewer returns `STATUS: PASS`
2. Reviewer returns `STATUS: PARTIAL` with only NON-BLOCKING issues
3. Maximum iterations reached (recommend: 3-5, configurable)
4. User explicitly accepts remaining issues

If max iterations reached without PASS:
```
STATUS: PARTIAL
FILE: {WORKFLOW_DIR}/performance.md
SUMMARY: Max iterations reached with {X} BLOCKING issues remaining
NEXT_INPUT: {WORKFLOW_DIR}/performance.md
---
- Loop exhausted after {N} iterations
- Remaining BLOCKING: {list}
- User decision required: accept or abort
```

---

## Handling File Errors

### Missing Input Files

When an agent attempts to read a required input file that doesn't exist:

### Step 1: List Directory Contents

```bash
ls -la {WORKFLOW_DIR}/
```

### Step 2: Identify Alternatives

Check if the required file exists under a different name or iteration:
- Expected: `{WORKFLOW_DIR}/performance.md`
- Found: `{WORKFLOW_DIR}/perf.md` or `{WORKFLOW_DIR}/performance-review.md`

Common mismatches:
- Abbreviated names (`perf` vs `performance`)
- Missing iteration suffix (`-review-2` vs `-2`)
- Typos in name

### Step 3: Decision

**If alternative file found:**
- Use the identified file
- Log the discrepancy in the report's Handoff Notes:
  ```
  ## Handoff Notes
  - WARNING: Expected `{WORKFLOW_DIR}/performance.md`, used `{WORKFLOW_DIR}/perf.md` instead
  ```

**If no matching file exists:**

The agent MUST stop and return an error status:

```
STATUS: ERROR
FILE: none
SUMMARY: Required input file missing: {WORKFLOW_DIR}/implementation.md
NEXT_INPUT: none
---
- Expected file: {WORKFLOW_DIR}/implementation.md
- Files in {WORKFLOW_DIR}/: [list actual files found]
- Cannot proceed without this input
- WORKFLOW HALTED - orchestrator must investigate
```

### Orchestrator Response to ERROR

When orchestrator receives `STATUS: ERROR`:

1. **Do NOT proceed to next step**
2. **Do NOT retry the same agent** (it will fail again)
3. **Investigate the cause:**
   - Was a previous step skipped?
   - Did a previous agent fail to write its output?
   - Is there a step number mismatch?
4. **Report to user:**
   ```
   WORKFLOW HALTED

   Agent: {agent-name}
   Missing file: {file path}
   Workflow directory: {WORKFLOW_DIR}

   Available files in {WORKFLOW_DIR}/:
   - {list files}

   Possible causes:
   - Step {N} may have failed silently
   - File naming mismatch

   To recover:
   - Re-run step {N} to regenerate the missing file
   - Or manually create the required file
   ```

### Prevention: Verify Output After Each Step

After the signal file appears, the orchestrator SHOULD verify the full report file exists:

```
# Wait for signal file
${CLAUDE_PLUGIN_ROOT}/scripts/wait-for-report.sh {WORKFLOW_DIR}/{name}-report.md

# Read the signal file
Read: {WORKFLOW_DIR}/{name}-report.md

# Parse the FILE from signal
expected_file = parse FILE field from signal

# Verify full report exists before proceeding
if not file_exists(expected_file):
    HALT with error: "Agent claimed to write {expected_file} but file not found"
```

This catches silent failures early rather than discovering them in later steps.

---

### Write Failures

When an agent cannot create or write to its output file:

**Common causes:**
- Permission denied (directory not writable)
- `{WORKFLOW_DIR}/` directory doesn't exist
- Disk full
- Path contains invalid characters
- File locked by another process

**Agent behavior on write failure:**

### Step 1: Attempt Recovery

If `{WORKFLOW_DIR}/` doesn't exist, try to create it:
```bash
mkdir -p {WORKFLOW_DIR}
```

If permission denied, check current directory:
```bash
pwd
ls -la | grep .workflow
```

### Step 2: If Recovery Fails

The agent MUST return an error status (do NOT return DONE/PASS with a non-existent file):

```
STATUS: ERROR
FILE: none
SUMMARY: Cannot write output file: {WORKFLOW_DIR}/implementation.md
NEXT_INPUT: none
---
- Attempted to write: {WORKFLOW_DIR}/implementation.md
- Error: Permission denied (or: Directory does not exist, etc.)
- Recovery attempted: mkdir -p {WORKFLOW_DIR}/ → failed
- Current directory: /path/to/repo
- WORKFLOW HALTED - orchestrator must investigate
```

### Step 3: Do NOT Fake Success

**Critical:** Never return `STATUS: DONE` or `STATUS: PASS` if the output file was not successfully written. This will cause cascading failures when the next agent tries to read the file.

Bad (causes downstream failure):
```
STATUS: DONE
FILE: {WORKFLOW_DIR}/implementation.md  ← file doesn't actually exist!
SUMMARY: Implementation complete
```

Good (halts immediately with clear error):
```
STATUS: ERROR
FILE: none
SUMMARY: Write failed: {WORKFLOW_DIR}/implementation.md - Permission denied
```

### Orchestrator Response to Write Failures

When orchestrator receives `STATUS: ERROR` due to write failure:

1. **HALT workflow immediately**
2. **Check directory permissions:**
   ```bash
   ls -la {WORKFLOW_DIR}/
   touch {WORKFLOW_DIR}/test-write && rm {WORKFLOW_DIR}/test-write
   ```
3. **Report to user:**
   ```
   WORKFLOW HALTED - Write Failure

   Agent: {agent-name}
   Workflow directory: {WORKFLOW_DIR}
   Could not write: {file path}
   Error: {error message}

   To recover:
   - Check directory permissions: ls -la {WORKFLOW_DIR}/
   - Ensure directory exists: mkdir -p {WORKFLOW_DIR}
   - Check disk space: df -h .
   - Re-run the failed step after fixing permissions
   ```

---

## Orchestrator Decision Logic

The orchestrator uses STATUS to decide next action:

| Status | Orchestrator Action |
|--------|---------------------|
| DONE | Proceed to next step |
| PASS | Proceed to next step |
| PARTIAL | Enter fix loop (may proceed with warnings) |
| FAIL | Enter fix loop (must fix before proceeding) |
| ERROR | **HALT workflow** - missing file or critical failure |

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
