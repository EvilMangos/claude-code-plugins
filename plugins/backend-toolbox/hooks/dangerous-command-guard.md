---
name: dangerous-command-guard
description: Guards against potentially dangerous bash commands
hooks:
  - event: PreToolUse
    tools: [ Bash ]
---

# Dangerous Command Guard Hook

Validates bash commands before execution to prevent accidental damage.

## Decision rules (deterministic)

- **BLOCK**: Do not run the command. Require user confirmation with the exact format below.
- **WARN**: Allow only after user confirmation with the exact format below.
- **ALLOW**: Run without extra confirmation.

### Confirmation protocol (exact)

When a command is BLOCKED or WARNed, require the user to reply with:

```
CONFIRM: <exact command text>
```

If the user confirms, re-run the exact command unchanged.

## Blocked Patterns

### Git Destructive Operations

Block these unless user explicitly confirms:

- `git push --force` or `git push -f` - **ALWAYS WARN**
- `git push --force` or `git push -f` to `main` or `master` - **BLOCK** (pattern: `git push.*--force.*(main|master)` or
  `git push.*-f.*(main|master)`)
- `git reset --hard` (without recent commit reference)
- `git clean -fd` or `git clean -fdx`
- `git checkout .` (discards all changes)
- `git filter-branch` / `git filter-repo` - **WARN** (history rewrite)
- `git rebase --onto` / large interactive rebases - **WARN** (history rewrite)

Message for force push to main/master: "Force pushing to main/master is destructive and affects other developers. Use a
feature branch instead."

Message for other destructive operations: "This is a destructive git operation. Please confirm you want to proceed."

### File System Dangers

Block or warn for:

- `rm -rf /` or `rm -rf /*` - **ALWAYS BLOCK**
- `rm -rf --no-preserve-root` - **ALWAYS BLOCK**
- `rm -rf ~` - **WARN** (can wipe user home)
- `rm -rf` on paths outside the project - **WARN**
- `rm -rf ..` or `rm -rf ../` - **WARN** (can escape project)
- `chmod -R 777` - **WARN** (security risk)
- `chmod -R` or `chown -R` on `/`, `~`, or other non-project roots - **WARN**
- `sudo` commands - **WARN** (elevated privileges)

Message: "This command could cause significant damage. Please review carefully."

### Disk / Device Dangers

- `dd` writing to raw devices (examples: `/dev/disk*`) - **ALWAYS BLOCK**
- `mkfs*` / `diskutil eraseDisk` - **ALWAYS BLOCK**

Message: "This command can irreversibly destroy disk data. Refuse unless the user explicitly confirms and understands
the target device."

### Remote Code Execution Footguns

- `curl ... | sh` / `wget ... | sh` / piping downloads into shells - **ALWAYS WARN**
- `bash -c "$(curl ...)"` and similar - **ALWAYS WARN**

Message: "Piping remote content into a shell is a common supply-chain/RCE risk. Prefer downloading, inspecting, then
executing."

### Fork Bomb / Resource Exhaustion

- Common fork bomb patterns (example: `:(){ :|:& };:`) - **ALWAYS BLOCK**

### Database Operations

Warn for:

- `DROP DATABASE`
- `DROP SCHEMA`
- `DROP TABLE`
- `TRUNCATE`
- `TRUNCATE.*CASCADE` - **EXTRA WARNING** (cascading can affect multiple tables)
- `DELETE FROM` without WHERE clause
- `dropdb` - **WARN**
- `psql.*DROP (DATABASE|SCHEMA|TABLE)` - **WARN**
- `mysql.*DROP (DATABASE|TABLE)` - **WARN**

Message: "This is a destructive database operation. Ensure you have backups."

Message for CASCADE operations: "This cascading operation could affect multiple tables. Verify the scope carefully."

### Secrets / Credential Exfiltration (warn)

Warn if a command appears to read common credential locations:

- `cat ~/.ssh/*`, `cat ~/.aws/*`, `cat ~/.config/*` (credential-like files)
- macOS Keychain access (`security find-*password*`) - **WARN**

Message: "This command may expose secrets/credentials. Avoid pasting secret contents into chat/logs. Prefer redaction or
referencing env var names."

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
To proceed: reply with `CONFIRM: <exact command>`
```

When warning:

```
WARNING: [reason]
Command: [the command]
Risk: [what could go wrong]
Proceed with caution. To proceed: reply with `CONFIRM: <exact command>`
```
