# Backend Toolbox Plugin

A comprehensive TDD and code quality framework for Claude Code.

## Philosophy

- Test-Driven Development (TDD) is mandatory
- Small, reversible steps with tests after each change
- Clear agent boundaries and responsibilities
- Quality gates at every stage

## Prerequisites

- CLAUDE.md for project-specific rules (for steward/curator agents)

## Agents (14)

### Core Workflow

| Agent                 | Role                              | Color   |
|-----------------------|-----------------------------------|---------|
| plan-creator          | Step-by-step implementation plans | magenta |
| business-analyst      | Requirements clarification        | cyan    |
| automation-qa         | Test design, RED stage            | blue    |
| tests-reviewer        | Test quality gate                 | cyan    |
| backend-developer     | Implementation, GREEN stage       | green   |
| acceptance-reviewer   | Functional completeness gate      | magenta |
| refactorer            | Behavior-preserving cleanup       | yellow  |
| code-reviewer         | Code quality gate                 | red     |
| documentation-updater | Doc sync                          | cyan    |

### Specialists

| Agent                           | Role                                    | Color  |
|---------------------------------|-----------------------------------------|--------|
| application-security-specialist | Vulnerability assessment, secure coding | red    |
| performance-specialist          | Bottleneck analysis, optimization       | yellow |
| devops-specialist               | CI/CD, Docker, Kubernetes, deployment   | blue   |

### Support

| Agent             | Role                   | Color  |
|-------------------|------------------------|--------|
| claude-md-steward | CLAUDE.md maintenance  | blue   |
| claude-curator    | .claude/** maintenance | yellow |

## Commands (8)

- `/complete-review` - Comprehensive code review (tests, quality, security, performance)
- `/develop-feature` - Full TDD workflow (planning, tests, implementation, review, docs)
- `/devops-change` - DevOps workflow for CI/CD, Docker, K8s, Terraform changes
- `/fix-bug` - Structured bug-fixing workflow (reproduction, root cause, TDD, review)
- `/refactor` - Behavior-preserving refactor with tests after each step
- `/refactor-tests` - Test-only refactoring (no production code changes)
- `/refresh-documentation` - Sync READMEs with repository reality
- `/refresh-claude-md` - Audit CLAUDE.md against repo state

## Skills (13)

### Testing & TDD

- **test-best-practices** - Behavior-focused testing, mocking, anti-patterns
- **tdd-workflow** - RED-GREEN-REFACTOR cycle, phase transitions

### Code Quality

- **refactoring-patterns** - Safe refactoring process, common patterns
- **design-patterns** - SOLID, DDD, dependency injection, design patterns
- **design-assessment** - Coupling/cohesion analysis, code smells
- **code-organization** - File structure, module boundaries, when to split code
- **code-review-checklist** - Systematic review workflow, quality checklist
- **quick-code-review** - Lightweight review for smaller changes
- **acceptance-criteria** - Requirement verification, completeness checking

### Security & Performance

- **web-api-security** - OWASP Top 10, injection patterns, secure coding
- **devops-infrastructure-security** - Secrets management, container hardening
- **backend-performance** - Database optimization, caching patterns
- **algorithm-efficiency** - Complexity analysis, data structures

## Typical Workflow

1. Run `/develop-feature [description]` or `/fix-bug [description]`
2. Plugin orchestrates: plan-creator -> automation-qa (RED) -> tests-reviewer -> backend-developer (GREEN) ->
   acceptance-reviewer -> refactorer -> code-reviewer -> documentation-updater

## Setup

1. Install the plugin
2. Optionally create CLAUDE.md for project-specific rules

## Installation

Install by copying or symlinking this folder into your Claude Code plugins location, or by referencing it from your
project's `.claude/plugins.json` (if you use project-scoped plugin config).

## Compatibility

This plugin ships a `.claude-plugin/plugin.json` intended for publishing/packaging. If your Claude Code runtime expects
a different manifest schema, adjust it to match your target environment.

## Releases

See `CHANGELOG.md` for version history.
