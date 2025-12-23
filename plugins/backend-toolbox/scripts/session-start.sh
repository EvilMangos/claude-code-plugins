#!/bin/bash

# Session start hook - checks for /run-tests command prerequisite

input=$(cat)
cwd=$(echo "$input" | jq -r '.cwd // ""')

# Silent exit if no cwd
[ -z "$cwd" ] && exit 0

# Check if this is a software project (has common project files)
has_project_file=false
for f in package.json Cargo.toml go.mod pyproject.toml Gemfile requirements.txt pom.xml build.gradle; do
  [ -f "$cwd/$f" ] && has_project_file=true && break
done

# Also check for source directories
if [ "$has_project_file" = false ]; then
  for d in src lib app; do
    [ -d "$cwd/$d" ] && has_project_file=true && break
  done
fi

# Silent exit if not a software project
[ "$has_project_file" = false ] && exit 0

# Check for /run-tests command
if [ -f "$cwd/.claude/commands/run-tests.md" ]; then
  echo "/run-tests command found - TDD workflows ready"
else
  cat <<'EOF'
Workflow Prerequisite Check

The backend-toolbox workflows (develop-feature, refactor, refactor-tests) require a /run-tests command.

To set up:
1. Create `.claude/commands/run-tests.md` in your project
2. Wrap your test runner (pytest, jest, go test, cargo test, etc.)
3. Accept optional path/pattern arguments

Example run-tests.md:
---
description: Run tests
argument-hint: [path-or-pattern]
allowed-tools: Bash
---
Run the project's test suite with: `npm test $ARGUMENTS` (or your test command)
EOF
fi

exit 0
