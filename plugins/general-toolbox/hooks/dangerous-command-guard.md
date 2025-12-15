---
name: dangerous-command-guard
description: Guards against potentially dangerous bash commands
hooks:
  - event: PreToolUse
    tools: [Bash]
---

# Dangerous Command Guard Hook

Validates bash commands before execution to prevent accidental damage.

## Blocked Patterns

### Git Destructive Operations
Block these unless user explicitly confirms:
- `git push --force` or `git push -f` - **ALWAYS WARN**
- `git push --force` or `git push -f` to `main` or `master` - **BLOCK** (pattern: `git push.*--force.*(main|master)` or `git push.*-f.*(main|master)`)
- `git reset --hard` (without recent commit reference)
- `git clean -fd` or `git clean -fdx`
- `git checkout .` (discards all changes)

Message for force push to main/master: "Force pushing to main/master is destructive and affects other developers. Use a feature branch instead."

Message for other destructive operations: "This is a destructive git operation. Please confirm you want to proceed."

### File System Dangers
Block or warn for:
- `rm -rf /` or `rm -rf /*` - **ALWAYS BLOCK**
- `rm -rf` on paths outside the project - **WARN**
- `chmod -R 777` - **WARN** (security risk)
- `sudo` commands - **WARN** (elevated privileges)

Message: "This command could cause significant damage. Please review carefully."

### Database Operations
Warn for:
- `DROP DATABASE`
- `DROP SCHEMA`
- `DROP TABLE`
- `TRUNCATE`
- `TRUNCATE.*CASCADE` - **EXTRA WARNING** (cascading can affect multiple tables)
- `DELETE FROM` without WHERE clause

Message: "This is a destructive database operation. Ensure you have backups."

Message for CASCADE operations: "This cascading operation could affect multiple tables. Verify the scope carefully."

## Allowed Patterns

These are generally safe and should not be blocked:
- `git status`, `git log`, `git diff`
- `git add`, `git commit`
- `git push` (without --force to non-protected branches)
- `ls`, `cat`, `find`, `grep`
- Test runners
- Build commands

## Response Format

When blocking:
```
BLOCKED: [reason]
Command: [the command]
Risk: [what could go wrong]
Alternative: [safer alternative if applicable]
```

When warning:
```
WARNING: [reason]
Command: [the command]
Risk: [what could go wrong]
Proceed with caution. Confirm to continue.
```
