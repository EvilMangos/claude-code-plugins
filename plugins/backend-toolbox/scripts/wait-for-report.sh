#!/bin/bash
# wait-for-report.sh - Remove stale report(s) and wait for new one(s)
#
# Usage: wait-for-report.sh [--interval N] <report-file> [report-file2 ...]
#   --interval N:  Seconds between checks (default: 10)
#   report-file:   Path(s) to the -report.md file(s) to wait for
#
# Examples:
#   wait-for-report.sh .workflow/task-123/implementation-report.md
#   wait-for-report.sh --interval 5 .workflow/task-123/performance-report.md .workflow/task-123/security-report.md

set -e

POLL_INTERVAL=10
FILES=()

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --interval)
      POLL_INTERVAL="$2"
      shift 2
      ;;
    *)
      FILES+=("$1")
      shift
      ;;
  esac
done

if [ ${#FILES[@]} -eq 0 ]; then
  echo "ERROR: At least one report file path required" >&2
  echo "Usage: wait-for-report.sh [--interval N] <report-file> [report-file2 ...]" >&2
  exit 1
fi

# Remove stale reports from previous iteration
for FILE in "${FILES[@]}"; do
  rm -f "$FILE"
done

# Poll until all report files appear
all_ready() {
  for FILE in "${FILES[@]}"; do
    [ ! -f "$FILE" ] && return 1
  done
  return 0
}

while ! all_ready; do
  sleep "$POLL_INTERVAL"
done

echo "Reports ready: ${FILES[*]}"
