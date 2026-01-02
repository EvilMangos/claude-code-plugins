#!/usr/bin/env bash
# Save a workflow signal to file
# Usage: save-signal.sh <taskId> <signalType> <status> <summary>
# Note: Does NOT update metadata step - step progression is handled by wait-signal
# to properly support parallel steps (increment once after ALL signals received)

set -e

# Source shared base directory helper
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_base-dir.sh"

TASK_ID="$1"
SIGNAL_TYPE="$2"
ARG3="$3"
ARG4="$4"

if [[ -z "$TASK_ID" || -z "$SIGNAL_TYPE" || -z "$ARG3" ]]; then
    echo '{"success":false,"error":"Missing required parameters: taskId, signalType, and status"}' >&2
    exit 1
fi

# Valid signal types
VALID_TYPES="requirements codebase-analysis plan tests-design tests-review implementation stabilization acceptance performance security refactoring code-review documentation finalize"
if [[ ! " $VALID_TYPES " =~ " $SIGNAL_TYPE " ]]; then
    echo "{\"success\":false,\"error\":\"Invalid signalType: $SIGNAL_TYPE\"}" >&2
    exit 1
fi

# Parse status and summary - support both formats:
# Format 1: save-signal.sh taskId type passed "summary"
# Format 2: save-signal.sh taskId type '{"status": "passed", "summary": "..."}'
if [[ "$ARG3" == "passed" || "$ARG3" == "failed" ]]; then
    STATUS="$ARG3"
    SUMMARY="$ARG4"
elif [[ "$ARG3" == \{* ]]; then
    # JSON format - parse with jq
    if command -v jq &> /dev/null; then
        STATUS=$(echo "$ARG3" | jq -r '.status // empty')
        SUMMARY=$(echo "$ARG3" | jq -r '.summary // empty')
    else
        # Fallback: simple regex extraction
        STATUS=$(echo "$ARG3" | grep -o '"status"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"\([^"]*\)"$/\1/')
        SUMMARY=$(echo "$ARG3" | grep -o '"summary"[[:space:]]*:[[:space:]]*"[^"]*"' | sed 's/.*"\([^"]*\)"$/\1/')
    fi
else
    STATUS="$ARG3"
    SUMMARY="$ARG4"
fi

# Valid statuses
if [[ "$STATUS" != "passed" && "$STATUS" != "failed" ]]; then
    echo "{\"success\":false,\"error\":\"Invalid status: $STATUS. Must be 'passed' or 'failed'\"}" >&2
    exit 1
fi

# Create directory structure
SIGNALS_DIR="${TASK_REPORTS_BASE}/${TASK_ID}/signals"
mkdir -p "$SIGNALS_DIR"

# Save signal as JSON
SIGNAL_FILE="${SIGNALS_DIR}/${SIGNAL_TYPE}.json"
cat > "$SIGNAL_FILE" <<EOF
{
  "status": "$STATUS",
  "summary": "$SUMMARY",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

echo "{\"success\":true,\"path\":\"$SIGNAL_FILE\"}"
