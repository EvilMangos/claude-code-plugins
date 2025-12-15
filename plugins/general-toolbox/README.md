# General Toolbox Plugin

A comprehensive TDD and code quality framework for Claude Code.

## Philosophy

- Test-Driven Development (TDD) is mandatory
- Small, reversible steps with tests after each change
- Clear agent boundaries and responsibilities
- Quality gates at every stage

## Prerequisites

- `/run-tests` command in target project's `.claude/commands/run-tests.md`
- CLAUDE.md for project-specific rules (for steward/curator agents)

## Agents (10)

### Core Workflow

| Agent | Role | Color |
|-------|------|-------|
| plan-creator | Step-by-step implementation plans | magenta |
| automation-qa | Test design, RED stage | blue |
| tests-reviewer | Test quality gate | cyan |
| feature-developer | Implementation, GREEN stage | green |
| acceptance-reviewer | Functional completeness gate | magenta |
| refactorer | Behavior-preserving cleanup | yellow |
| code-reviewer | Code quality gate | red |
| documentation-updater | Doc sync | cyan |

### Support

| Agent | Role | Color |
|-------|------|-------|
| claude-md-steward | CLAUDE.md maintenance | blue |
| claude-curator | .claude/** maintenance | yellow |

## Commands (5)

- `/develop-feature` - Full TDD workflow (planning, tests, implementation, review, docs)
- `/refactor` - Behavior-preserving refactor with tests after each step
- `/refactor-tests` - Test-only refactoring (no production code changes)
- `/refresh-documentation` - Sync READMEs with repository reality
- `/refresh-claude-md` - Audit CLAUDE.md against repo state

## Skills (6)

- **test-best-practices** - Behavior-focused testing, mocking, anti-patterns
- **tdd-workflow** - RED-GREEN-REFACTOR cycle, phase transitions
- **refactoring-patterns** - Safe refactoring process, common patterns
- **software-design-principles** - SOLID, coupling/cohesion, DDD, patterns
- **code-review-checklist** - Systematic review workflow, quality checklist
- **acceptance-criteria** - Requirement verification, completeness checking

## Hooks (4)

- **dangerous-command-guard** - Block destructive git/filesystem/database operations
- **test-reminder** - Remind to run tests after code modifications
- **session-start** - Verify prerequisites at session start
- **workflow-completion** - Generate structured summary when workflows complete

## Typical Workflow

1. Run `/develop-feature [description]`
2. Plugin orchestrates: plan-creator -> automation-qa (RED) -> tests-reviewer -> feature-developer (GREEN) -> acceptance-reviewer -> refactorer -> code-reviewer -> documentation-updater
3. workflow-completion hook generates final summary

## Setup

1. Install the plugin
2. Create `/run-tests` command in your project that wraps your test runner
3. Optionally create CLAUDE.md for project-specific rules
