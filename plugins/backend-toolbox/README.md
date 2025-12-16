# Backend Toolbox Plugin

A comprehensive TDD and code quality framework for Claude Code.

## Philosophy

- Test-Driven Development (TDD) is mandatory
- Small, reversible steps with tests after each change
- Clear agent boundaries and responsibilities
- Quality gates at every stage

## Prerequisites

- `/run-tests` command in target project's `.claude/commands/run-tests.md`
- CLAUDE.md for project-specific rules (for steward/curator agents)

## Agents (13)

### Core Workflow

| Agent | Role | Color |
|-------|------|-------|
| plan-creator | Step-by-step implementation plans | magenta |
| automation-qa | Test design, RED stage | blue |
| tests-reviewer | Test quality gate | cyan |
| backend-developer | Implementation, GREEN stage | green |
| acceptance-reviewer | Functional completeness gate | magenta |
| refactorer | Behavior-preserving cleanup | yellow |
| code-reviewer | Code quality gate | red |
| documentation-updater | Doc sync | cyan |

### Specialists

| Agent | Role | Color |
|-------|------|-------|
| security-specialist | Vulnerability assessment, secure coding | red |
| performance-specialist | Bottleneck analysis, optimization | yellow |
| devops-specialist | CI/CD, Docker, Kubernetes, deployment | blue |

### Support

| Agent | Role | Color |
|-------|------|-------|
| claude-md-steward | CLAUDE.md maintenance | blue |
| claude-curator | .claude/** maintenance | yellow |

## Commands (6)

- `/develop-feature` - Full TDD workflow (planning, tests, implementation, review, docs)
- `/fix-bug` - Structured bug-fixing workflow (reproduction, root cause, TDD, review)
- `/refactor` - Behavior-preserving refactor with tests after each step
- `/refactor-tests` - Test-only refactoring (no production code changes)
- `/refresh-documentation` - Sync READMEs with repository reality
- `/refresh-claude-md` - Audit CLAUDE.md against repo state

## Skills (12)

### Testing & TDD
- **test-best-practices** - Behavior-focused testing, mocking, anti-patterns
- **tdd-workflow** - RED-GREEN-REFACTOR cycle, phase transitions

### Code Quality
- **refactoring-patterns** - Safe refactoring process, common patterns
- **design-patterns** - SOLID, DDD, dependency injection, design patterns
- **design-assessment** - Coupling/cohesion analysis, code smells
- **code-review-checklist** - Systematic review workflow, quality checklist
- **quick-code-review** - Lightweight review for smaller changes
- **acceptance-criteria** - Requirement verification, completeness checking

### Security & Performance
- **web-api-security** - OWASP Top 10, injection patterns, secure coding
- **devops-infrastructure-security** - Secrets management, container hardening
- **backend-performance** - Database optimization, caching patterns
- **algorithm-efficiency** - Complexity analysis, data structures

## Hooks (5)

- **dangerous-command-guard** - Block destructive git/filesystem/database operations
- **test-reminder** - Remind to run tests after code modifications
- **validate-test-files** - Prevent inappropriate test file modifications
- **session-start** - Verify prerequisites at session start
- **workflow-completion** - Generate structured summary when workflows complete

## Typical Workflow

1. Run `/develop-feature [description]` or `/fix-bug [description]`
2. Plugin orchestrates: plan-creator -> automation-qa (RED) -> tests-reviewer -> backend-developer (GREEN) -> acceptance-reviewer -> refactorer -> code-reviewer -> documentation-updater
3. workflow-completion hook generates final summary

## Setup

1. Install the plugin
2. Create `/run-tests` command in your project that wraps your test runner
3. Optionally create CLAUDE.md for project-specific rules
