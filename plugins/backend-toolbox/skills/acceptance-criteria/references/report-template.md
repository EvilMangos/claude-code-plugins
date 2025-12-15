# Acceptance Review Report Template

Use this template when reporting acceptance review findings.

## Full Report Template

```markdown
## Acceptance Review Summary

**Request**: [Brief description of what was requested]
**Verdict**: PASS | PARTIAL | FAIL

### Instructions Mapping

| # | Instruction | Status | Implementation | Notes |
|---|-------------|--------|----------------|-------|
| 1 | [Explicit instruction from request] | ✅ Done | `file.ts:42` | |
| 2 | [Another instruction] | ⚠️ Partial | `component.tsx:15` | Missing X |
| 3 | [Implicit instruction] | ❌ Missing | - | Not implemented |

### Gaps

1. **[Gap Title]**
   - **Type**: Missing | Incomplete | Different | Assumption
   - **Requested**: [What the request asked for]
   - **Implemented**: [What was actually done]
   - **Impact**: [How this affects meeting the request]

2. **[Another Gap]**
   - ...

### Assumptions Made

| Assumption | Basis | Risk if Wrong |
|------------|-------|---------------|
| [What was assumed] | [Why this assumption was made] | [Consequence] |

### Open Questions

- [ ] [Question requiring clarification]
- [ ] [Another question]

### Recommendation

[Clear statement: proceed as-is, what needs to be addressed, or what needs clarification]
```

## Condensed Report Template

For smaller reviews:

```markdown
## Acceptance Review: [Request Summary]

**Verdict**: PASS | PARTIAL | FAIL

### Instructions
- [x] Instruction 1 - `file.ts:42`
- [ ] Instruction 2 - Missing
- [~] Instruction 3 - Partial: needs X

### Gaps
1. [Gap]: [What's needed]

### Action Items
- [ ] [What needs to happen next]
```

## Verdict Definitions

| Verdict | Meaning | Action |
|---------|---------|--------|
| **PASS** | All instructions from request satisfied | Complete |
| **PARTIAL** | Most instructions met, some gaps remain | Address gaps or confirm acceptable |
| **FAIL** | Critical instructions not satisfied | Must address before proceeding |
