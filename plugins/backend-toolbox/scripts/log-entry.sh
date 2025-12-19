#!/bin/bash
# log-entry.sh - Append a timestamped log entry to a workflow logs file
#
# Usage: log-entry.sh <log-file> <action-type> <message>
#
# Arguments:
#   log-file:     Path to the -logs.md file (e.g., .workflow/task-123/implementation-logs.md)
#   action-type:  One of: STARTED, READ_FILE, TOOL_CALL, DECISION, WRITE_FILE, COMPLETED, ERROR
#   message:      The log message (can be multi-line if quoted)
#
# The script automatically:
#   - Creates the log file if it doesn't exist
#   - Adds ISO 8601 timestamp
#   - Formats as markdown heading
#
# Examples:
#   log-entry.sh .workflow/task-123/impl-logs.md STARTED "Agent: backend-developer\nTask: Implement auth"
#   log-entry.sh .workflow/task-123/impl-logs.md TOOL_CALL "Tool: Write\nFile: src/auth.ts"
#   log-entry.sh .workflow/task-123/impl-logs.md COMPLETED "Status: DONE\nTests: 5/5 passing"

set -e

if [ $# -lt 3 ]; then
  echo "ERROR: Missing required arguments" >&2
  echo "Usage: log-entry.sh <log-file> <action-type> <message>" >&2
  echo "" >&2
  echo "Action types: STARTED, READ_FILE, TOOL_CALL, DECISION, WRITE_FILE, COMPLETED, ERROR" >&2
  exit 1
fi

LOG_FILE="$1"
ACTION_TYPE="$2"
MESSAGE="$3"

# Validate action type
case "$ACTION_TYPE" in
  STARTED|READ_FILE|TOOL_CALL|DECISION|WRITE_FILE|COMPLETED|ERROR)
    ;;
  *)
    echo "WARNING: Unknown action type '$ACTION_TYPE'. Valid types: STARTED, READ_FILE, TOOL_CALL, DECISION, WRITE_FILE, COMPLETED, ERROR" >&2
    ;;
esac

# Get ISO 8601 timestamp
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Ensure parent directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Append log entry (interpret \n as newlines)
{
  echo ""
  echo "## [$TIMESTAMP] $ACTION_TYPE"
  echo -e "$MESSAGE"
} >> "$LOG_FILE"

echo "Logged: [$TIMESTAMP] $ACTION_TYPE -> $LOG_FILE"
