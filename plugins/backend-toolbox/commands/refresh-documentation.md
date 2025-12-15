---
description: Refresh README documentation under a given path (file or folder).
argument-hint: <path-to-README-or-folder>
allowed-tools: Read, Edit, Grep, Glob, Bash(find:*), Bash(ls:*), Bash(cat:*), Bash(rg:*), Bash(git:*), Bash(sed:*), Bash(awk:*), SlashCommand, Task
---

You are running a **documentation refresh** workflow.

Input:
> $ARGUMENTS

`$ARGUMENTS` is required and must be either:

- a path to a single `README.md`, or
- a folder path, in which case you must update **all nested `README.md`** files under that folder (recursive).

## Hard constraints

- You may edit **only** files named exactly `README.md`.
- Do not edit source code, tests, CI, or any other docs (including `CLAUDE.md`) in this command.
- Apply minimal diffs. Preserve existing structure and tone unless it is clearly outdated/confusing.
- Do not invent commands, paths, scripts, or behavior. If you cannot verify something, mark it as TODO or remove it.

## Execution workflow (strict)

### 1) Preflight

1. If `$ARGUMENTS` is empty: STOP and ask the user to provide a path.
2. Verify the path exists:
    - `ls -la "$ARGUMENTS"`

### 2) Collect target README files

Determine targets in this order:

1. If `$ARGUMENTS` is a `README.md` file:
    - Use:
        - `find "$ARGUMENTS" -maxdepth 0 -type f -name README.md -print`
    - If it returns a path, set that as the only target.

2. Otherwise treat `$ARGUMENTS` as a directory scope and find nested READMEs:
    - Use a pruned find to avoid vendor/build dirs:
        - `find "$ARGUMENTS" \
        \( -path '*/.git/*' -o -path '*/node_modules/*' -o -path '*/dist/*' -o -path '*/build/*' -o -path '*/.venv/*' -o -path '*/vendor/*' \) -prune -o \
        -type f -name README.md -print`

3. If the target list is empty: STOP and report “No README.md files found under the provided path.”

### 3) Refresh each README.md (loop over targets)

For each `README.md` target:

1. Read the README content.

2. Identify claims that must match repo reality (only what the README already mentions):
    - Commands to run (dev/test/lint/build/migrate/seed/examples)
    - File paths / module locations
    - Environment variables and config file names
    - “How to run” steps
    - References to scripts/manifests/tooling

3. Verify each claim using repo evidence:
    - `rg` for referenced script names, CLI commands, env vars, and file paths
    - `ls` / `find` for referenced paths and files
    - `cat` for referenced manifests/configs that the README points to
    - If the README mentions “run X”, verify X exists (script/task/make target/etc.) and the arguments look plausible

4. Edit the README with minimal diffs:
    - Fix broken paths, renamed scripts, incorrect flags, outdated examples
    - Remove or downgrade unverifiable claims (replace with TODO) rather than guessing
    - Keep formatting consistent (headings, lists, code blocks)

5. After edits:
    - Show the diff for this README:
        - `git diff -- "$README_PATH"`
    - Ensure you did not modify any non-README files:
        - `git diff --name-only`

   If any changed file is not exactly `README.md`:
    - Revert immediately and STOP:
        - `git restore --staged --worktree .`
        - Explain which file violated the constraint.

### 4) Final output

Return:

- List of README.md files updated
- Bullet summary of what changed per file (2–6 bullets each)
- Any TODOs you inserted because something could not be verified
