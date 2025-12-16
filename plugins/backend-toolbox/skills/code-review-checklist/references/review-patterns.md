# Code Review Patterns

Common review scenarios and strategies for effective feedback.

## Review by Change Type

### Bug Fix Reviews

Focus areas:

- Root cause identification - does the fix address the actual problem or just symptoms?
- Regression risk - could this fix break other functionality?
- Test coverage - is there a test that would have caught this bug?

Questions to ask:

- What caused this bug originally?
- Are there similar patterns elsewhere that might have the same issue?
- Does the fix handle all edge cases of this bug?

### Feature Addition Reviews

Focus areas:

- API design - is the interface intuitive and consistent with existing patterns?
- Extensibility - can this feature evolve without major rewrites?
- Documentation - are new behaviors documented?

Questions to ask:

- How does this integrate with existing features?
- What happens when this feature is disabled/unavailable?
- Are error states handled gracefully?

### Refactoring Reviews

Focus areas:

- Behavioral preservation - does the code still do what it did before?
- Test coverage - are existing tests passing without modification?
- Incremental changes - is this a reasonable-sized change to review?

Questions to ask:

- What motivated this refactoring?
- Are there benchmarks showing no performance regression?
- Could this be split into smaller, safer changes?

### Performance Optimization Reviews

Focus areas:

- Benchmarks - are there before/after measurements?
- Readability trade-offs - is the complexity justified by the gains?
- Edge cases - does the optimization hold for all input sizes?

Questions to ask:

- What workload was used to measure improvement?
- Is this optimization in a hot path that justifies complexity?
- Are there simpler alternatives with similar gains?

## Handling Common Situations

### Large PRs (500+ lines)

Strategy:

1. Request the PR be split if possible
2. If not splittable, review in logical chunks
3. Focus on architecture first, then details
4. Use multiple review sessions if needed

Comment template:

> This PR is quite large. Could we split it into [suggested split]? If not, I'll review it in stages focusing on [area] first.

### Disagreement on Approach

Strategy:

1. Understand the author's reasoning first
2. Present alternatives with concrete trade-offs
3. Distinguish preferences from requirements
4. Escalate to team discussion if needed

Comment template:

> I see why you chose [approach]. I'm wondering about [alternative] because [reasoning]. What do you think about the trade-offs here?

### Repeated Issues

Strategy:

1. Address pattern, not just instance
2. Suggest tooling/linting if applicable
3. Consider creating team guidelines
4. Link to documentation

Comment template:

> I've noticed [pattern] in a few places. This often leads to [problem]. Consider [solution]. We might want to add a lint rule for this.

### Junior Developer Code

Strategy:

1. Be encouraging while maintaining standards
2. Explain the "why" behind suggestions
3. Prioritize learning opportunities
4. Pair on complex fixes if needed

Comment template:

> Good start! One thing to consider: [suggestion]. This matters because [explanation]. Happy to pair on this if helpful.

## Feedback Tone Guide

### Phrasing That Works

| Instead of...       | Try...                                |
| ------------------- | ------------------------------------- |
| "This is wrong"     | "This might cause [issue] because..." |
| "You should..."     | "Consider..." or "What about..."      |
| "Why didn't you..." | "I'm curious about the choice to..."  |
| "Obviously..."      | (Just state the fact)                 |
| "Just do X"         | "One option: X, which would..."       |

### Marking Severity

Use prefixes to indicate importance:

- `[blocking]` - Must fix before merge
- `[suggestion]` - Nice to have, author decides
- `[question]` - Seeking understanding
- `[nit]` - Minor style/preference issue
- `[praise]` - Highlighting good work

### When to Approve

Approve when:

- All blocking issues are resolved
- You understand the change well enough to support it
- Tests are adequate for the change scope
- You'd be comfortable debugging this code

Don't block on:

- Style preferences not in team guidelines
- Hypothetical future issues
- Personal preferences for different approaches
- "I would have done it differently"

## Review Efficiency Tips

### First Pass (5-10 minutes)

1. Read PR description and linked issues
2. Scan file list for scope
3. Look at test changes first
4. Identify areas needing deep review

### Deep Review (varies)

1. Start from entry points
2. Follow data flow through changes
3. Check error handling paths
4. Verify edge cases in tests

### Final Pass (5 minutes)

1. Re-read your comments for tone
2. Verify blocking vs non-blocking labels
3. Add summary if many comments
4. Approve or request changes

## Anti-Patterns to Avoid

### Gatekeeping

- Blocking on non-issues to assert authority
- Requiring "your way" when alternatives work
- Adding unnecessary process

### Drive-by Reviewing

- Surface-level comments without deep review
- Approving without understanding
- Rubber-stamping to avoid conflict

### Nitpick Storms

- Many minor comments overwhelming real issues
- Style policing beyond team standards
- Perfectionism blocking progress

### Ghost Reviews

- Starting review but never completing
- Requesting changes without follow-up
- Leaving PR in limbo
