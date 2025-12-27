# Backend Toolbox Plugin

Toolbox that consists of skills, agents and commands for backend development

## Philosophy

- Test-Driven Development (TDD) is mandatory
- Small, reversible steps with tests after each change
- Clear agent boundaries and responsibilities
- Quality gates at every stage

## Prerequisites

- CLAUDE.md for project-specific rules (for steward/curator agents)

## Agents (15)

### Core Workflow

| Agent                 | Role                              | Color   |
|-----------------------|-----------------------------------|---------|
| plan-creator          | Step-by-step implementation plans | magenta |
| business-analyst      | Requirements clarification        | cyan    |
| codebase-analyzer     | Pattern & convention discovery    | cyan    |
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

- `/complete-review` - Review code for quality, security, and performance issues (defaults to staged/unstaged git changes)
- `/develop-feature` - End-to-end TDD workflow (planning, test design, test review, implementation, acceptance, performance, security, refactoring, code review, docs)
- `/devops-change` - DevOps changes (CI/CD, Docker, K8s, Terraform) with planning and review workflow
- `/fix-bug` - Structured bug-fixing workflow (reproduction, root cause analysis, TDD, implementation, code review)
- `/refactor` - Refactor code in a path with tests after each step (never modify test files)
- `/refactor-tests` - Refactor tests within a path (never modify production code)
- `/refresh-documentation` - Refresh README documentation under a given path
- `/refresh-claude-md` - Audit CLAUDE.md against repo reality

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

## Hooks (1)

| Hook             | Event      | Matcher | Purpose                                                     |
|------------------|------------|---------|-------------------------------------------------------------|
| I/O tools inject | PreToolUse | Task    | Injects I/O tool instructions into backend-toolbox subagent prompts |

The hook ensures all backend-toolbox subagents use workflow I/O tools (`save-report`, `save-signal`, `get-report`, `wait-signal`) for workflow state persistence.

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

