#!/usr/bin/env bash
# Shared helper to get the base directory for task reports
# All workflow-io scripts should source this file
#
# Uses (in order of priority):
# 1. TASK_REPORTS_DIR environment variable (if set)
# 2. Git repository root + .task-reports (if in a git repo)
# 3. Current working directory + .task-reports (fallback)
#
# Sets: TASK_REPORTS_BASE (absolute path to .task-reports directory)

get_task_reports_base() {
    # 1. Check for explicit environment variable
    if [[ -n "$TASK_REPORTS_DIR" ]]; then
        echo "$TASK_REPORTS_DIR"
        return
    fi

    # 2. Try to find git root
    local git_root
    git_root=$(git rev-parse --show-toplevel 2>/dev/null)
    if [[ -n "$git_root" ]]; then
        echo "${git_root}/.task-reports"
        return
    fi

    # 3. Fallback to current directory
    echo "${PWD}/.task-reports"
}

TASK_REPORTS_BASE=$(get_task_reports_base)
