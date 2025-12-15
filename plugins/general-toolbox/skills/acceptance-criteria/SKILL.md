---
name: acceptance-criteria
description: >
  This skill should be used when the user asks to "verify implementation", "check requirements",
  "validate completeness", "review acceptance criteria", "check if done", "verify changes meet
  the request", or needs to assess whether changes satisfy the original request instructions.
---

# Acceptance Criteria Verification

Verify that implementations fully satisfy all request instructions through systematic review.

## Core Workflow

1. **Extract instructions** from the original request
2. **Map each instruction** to its implementation
3. **Verify completeness** of each instruction
4. **Identify gaps** between request and implementation
5. **Report findings** with clear verdict

## Step 1: Extract Instructions

### Explicit Instructions
Parse the original request for direct statements:
- Feature requests: "Add a button that..."
- Behavioral requirements: "The system should..."
- Constraints: "Must work on mobile", "Should support X"
- Specific details: exact values, formats, behaviors mentioned

### Implicit Instructions
Identify unstated but clearly expected behaviors:
- Consistency with how the request was framed
- Obvious edge cases mentioned or implied
- Behaviors that logically follow from the request

### Ambiguous Areas
Flag vague terms that need clarification:
- "Fast" → What's the threshold?
- "User-friendly" → What specific behaviors?
- "Similar to X" → Which aspects exactly?

## Step 2: Map Instructions to Implementation

Create an instruction mapping table:

| # | Instruction | Status | Implementation | Notes |
|---|-------------|--------|----------------|-------|
| 1 | [From request] | ✅/⚠️/❌ | `file:line` | [Details] |

Status indicators:
- ✅ **Done** - Fully implemented as requested
- ⚠️ **Partial** - Implemented but incomplete or different from request
- ❌ **Missing** - Not implemented

## Step 3: Verify Completeness

For each instruction, verify:

| Check | Question |
|-------|----------|
| **Presence** | Is the functionality present in the code? |
| **Correctness** | Does it behave as requested? |
| **Completeness** | Are all aspects of the instruction covered? |
| **Consistency** | Does it match the intent of the request? |

## Step 4: Identify Gaps

Categorize each gap:

| Gap Type | Description |
|----------|-------------|
| **Missing** | Instruction not implemented at all |
| **Incomplete** | Only part of the instruction implemented |
| **Different** | Implemented differently than requested |
| **Assumption** | Implementation made assumptions not in request |

For each gap, note:
- What was requested vs what was implemented
- Impact on meeting the user's needs

## Step 5: Report Findings

Conclude with a clear verdict:

| Verdict | Meaning |
|---------|---------|
| **PASS** | All instructions satisfied |
| **PARTIAL** | Most instructions met, some gaps remain |
| **FAIL** | Critical instructions not satisfied |

## Quick Checklist

- [ ] All explicit instructions from request implemented
- [ ] Each instruction maps to specific implementation
- [ ] Implementation matches the requested behavior
- [ ] No instructions were overlooked or forgotten
- [ ] Assumptions documented if any were made

## Additional Resources

### Reference Files
- **`references/checklists.md`** - Detailed verification checklist
- **`references/report-template.md`** - Report templates

### Examples
- **`examples/review-example.md`** - Complete acceptance review example
