---
description: Audit CLAUDE.md against repo reality (everything it mentions).
allowed-tools: Read, Edit, Bash(git:*), Bash(ls:*), Bash(find:*), Bash(rg:*), Bash(cat:*), Bash(sed:*), Bash(awk:*), SlashCommand
---

You are running a **CLAUDE.md reality sync** workflow.

Goal: verify that **everything mentioned in `CLAUDE.md`** matches the current repository.
If not, update **only `CLAUDE.md`** with minimal diffs.

## Hard constraints

- You may read any files needed to verify facts.
- You may edit **only**: `CLAUDE.md`
- Do not edit `.claude/**`, source code, tests, CI, infra, or any other docs.

## Audit targets (only things that appear in CLAUDE.md)

For each target below: if `CLAUDE.md` mentions it, verify it exists and is correct (names, paths, commands).
If it is not mentioned in `CLAUDE.md`, do not add new topics/sections unless needed to fix an inaccuracy.

### 1) Repo identity & structure claims

- Project name(s), single app vs monorepo claim
- Any referenced top-level directories (`apps/`, `services/`, `packages/`, `docs/`, etc.)
- Any described components/services and their paths

Verification:

- `git ls-files`
- `ls` / `find` for referenced paths

### 2) Architecture claims

- Named services/components (API, workers, queues, DB, cache, background jobs)
- Integrations explicitly described (payment providers, email providers, auth, storage, analytics, etc.) if present

Verification:

- `rg` for referenced names/terms
- check referenced infra/config files if they’re explicitly mentioned

### 3) Commands & scripts (most common drift)

- Dev commands
- Test commands (unit/integration/e2e/etc.) and config file paths
- Lint/format commands
- Build/migrate/seed commands
- “Run a single test file” examples

Verification:

- Identify the repo’s command entrypoints referenced by CLAUDE.md (e.g., Makefile, task runner files, package manifests,
  build scripts)
- `cat` those manifests/scripts and confirm the documented commands exist and match
- `find`/`ls` for referenced config paths
- If multiple manifests exist, verify which one CLAUDE.md refers to

### 4) Environment variables & config

- Any env vars listed (names + meaning + required/optional)
- Referenced env files (`.env.example`, templates, config dirs/files)
- Local setup steps that depend on config/env

Verification:

- Confirm referenced env/config files exist
- Search the codebase for usage patterns appropriate to the repo’s languages/frameworks
  (don’t assume any specific language; choose patterns that actually appear in the repo)
- Cross-check that env vars mentioned in CLAUDE.md are actually used and that commonly-used ones
  aren’t inaccurately named in CLAUDE.md

### 5) Tooling & workflows

- CI references (e.g. `.github/workflows/*`) if CLAUDE.md mentions them
- Container references (`Dockerfile`, `docker-compose*.yml`, devcontainer, etc.) if mentioned
- Migration tooling (whatever the repo uses) if mentioned

Verification:

- `ls .github/workflows` (only if referenced)
- `ls Dockerfile docker-compose*.yml` (only if referenced)
- confirm referenced tooling/config paths exist

### 6) Concrete file paths shown in examples

- Any explicit file paths in code blocks or bullets
- Any “common locations” in text

Verification:

- `ls` those exact paths; correct typos/renames

### 7) .claude ecosystem references (read-only)

- Any mention of subagents/commands/plugins in CLAUDE.md
- Ensure names match actual files in `.claude/agents` and `.claude/commands`

Verification:

- `find .claude -maxdepth 3 -type f`
- compare referenced names to actual filenames

### 8) Links / external references (only if present)

- URLs claimed to be canonical (docs/runbooks)
- Remove/replace only if obviously incorrect/outdated in context

## Mismatch report format (required)

Produce a mismatch report grouped as:

- **Remove/Replace** (obsolete or renamed items)
- **Correct** (wrong paths, flags, script names)
- **Add** (only minimal additions required to make existing sections true/usable)

## Edit rules for CLAUDE.md (required)

- Apply the smallest set of edits to make `CLAUDE.md` accurate.
- Prefer in-place fixes and small bullet edits.
- Avoid rewriting the whole document.
- Do not create new major sections unless necessary to correct a claim that currently exists.

## Execution workflow (strict)

1) Read `CLAUDE.md` and extract:
    - headings (in order)
    - all code blocks
    - all shell commands (lines that look like CLI invocations)
    - all file paths (anything that looks like a path)
    - all env var names (e.g., `FOO_BAR`, `...FOO_BAR...` in code blocks/text)

2) Verify each extracted item against the repo using `rg`, `ls`, `find`, and any manifests/scripts the repo uses.

3) Produce the mismatch report.

4) Write a mini-plan:
    - which CLAUDE.md sections will change
    - exactly what will be edited (bullets)

5) Delegate the actual edit to `claude-md-steward`:
    - remind it: edit only `CLAUDE.md`, minimal diff

6) Re-check only the edited areas to confirm mismatches are resolved.

## Final output requirements

Return:

1) **Mismatch Report**
2) **Edit plan**
3) **What changed**
4) **Assumptions / Needs confirmation** (only if something couldn’t be verified; do not guess)
