---
description: Review code for quality, security, and performance issues. If no path is provided, reviews staged/unstaged git changes.
argument-hint: [ path ]
allowed-tools: Read, Glob, Grep, Bash(git:*), Task, Skill
---

You are orchestrating a **code review** workflow for this repository.

The user request is:

> $ARGUMENTS

The argument is an optional **path** to a file or folder. If no argument is provided, review the **current git changes** (staged and unstaged).

You MUST delegate the actual review work to the named subagents.
Do not do a subagent's work in the main agent.

Required subagents:

- codebase-analyzer
- tests-reviewer
- code-reviewer
- application-security-specialist
- performance-specialist

## Preflight (main agent)

1) Determine scope:
    - If `$ARGUMENTS` is empty: review current git changes (staged + unstaged)
    - Else: set scope to `$ARGUMENTS` (file or directory path)

2) Verify the scope exists:
    - If path provided: use Glob to verify the path exists
    - If reviewing git changes: run `git status` and `git diff --name-only` to identify changed files
    - If no changes found: STOP and inform the user there are no changes to review

3) Gather context:
    - For git changes: run `git diff` to get the actual diff content
    - For path: read the files in the specified path
    - Identify the primary language/framework being used

## Workflow

### 1) Codebase Analysis (delegate to `codebase-analyzer`)

Invoke `codebase-analyzer` with:

- The scope (path or list of changed files)
- Request analysis of the codebase to discover:
    - Existing patterns and conventions
    - Project-specific abstractions and utilities
    - Code organization and architecture style
    - Testing patterns and frameworks

This step provides context for all subsequent reviews. The analysis report will help reviewers:

- Identify violations of established conventions
- Check if new code follows existing patterns
- Verify proper use of project utilities
- Ensure consistency with codebase style

Collect the codebase analysis report for reference by other reviewers.

### 2) Test Review (delegate to `tests-reviewer`)

Invoke `tests-reviewer` with:

- The scope (path or list of changed files)
- The code content or diff to review
- Request evaluation of:
    - Test coverage for new/changed code
    - Test correctness and assertion quality
    - Test design and maintainability
    - Flakiness risks and determinism
    - Proper mocking and isolation

Collect test review findings including:

- Coverage gaps
- Test quality issues
- Recommendations for improvement

### 3) Code Quality Review (delegate to `code-reviewer`)

Invoke `code-reviewer` with:

- The scope (path or list of changed files)
- The code content or diff to review
- Request evaluation of:
    - Design & Architecture alignment
    - Readability & Maintainability
    - Test quality (if test files are in scope)
    - Error handling patterns

Collect the review output including:

- Summary of findings
- Issues to resolve

### 4) Security Review (delegate to `application-security-specialist`)

Invoke `application-security-specialist` with:

- The same scope and code content
- Request evaluation of:
    - OWASP Top 10 vulnerabilities
    - Input validation
    - Authentication/authorization patterns
    - Sensitive data handling
    - Injection vulnerabilities (SQL, XSS, command)

Collect security findings categorized by severity.

### 5) Performance Review (delegate to `performance-specialist`)

Invoke `performance-specialist` with:

- The same scope and code content
- Request evaluation of:
    - Algorithm efficiency
    - N+1 query patterns
    - Resource management
    - Memory/CPU considerations
    - Caching opportunities

Collect performance findings and recommendations.

### 6) Synthesize Final Report (main agent)

Combine all subagent findings into a unified report:

```markdown
## Code Review Summary

**Scope**: [path or "git changes"]
**Files Reviewed**: [count]

## Issues (All Must Be Resolved)

[List all issues from all reviews - code quality, test quality, security, performance]

## Verdict

- [ ] **APPROVED** - No issues found, ready to merge
- [ ] **NEEDS CHANGES** - Issues must be addressed first
```

Mark the appropriate verdict checkbox based on findings.
