#!/bin/bash
# remove-report.sh - Remove report file(s) before launching a new agent
#
# Usage: remove-report.sh <report-file> [report-file2 ...]
#   report-file:   Path(s) to the -report.md file(s) to remove
#
# Use this script BEFORE launching a background agent to ensure
# wait-for-report.sh waits for a fresh report, not a stale one.
#
# Examples:
#   remove-report.sh .workflow/task-123/implementation-report.md
#   remove-report.sh .workflow/task-123/performance-report.md .workflow/task-123/security-report.md

set -e

if [ $# -eq 0 ]; then
  echo "ERROR: At least one report file path required" >&2
  echo "Usage: remove-report.sh <report-file> [report-file2 ...]" >&2
  exit 1
fi

for FILE in "$@"; do
  rm -f "$FILE"
done

echo "Removed: $*"
