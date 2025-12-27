#!/usr/bin/env bash
# Create task metadata with execution steps
# Usage: create-metadata.sh <taskId> <executionSteps>
# executionSteps is a JSON array, e.g.: '["plan","tests-design",["performance","security"],"implementation"]'
# Arrays within the steps array represent parallel steps

set -e

TASK_ID="$1"
EXECUTION_STEPS="$2"

if [[ -z "$TASK_ID" || -z "$EXECUTION_STEPS" ]]; then
    echo '{"success":false,"error":"Missing required parameters: taskId and executionSteps"}' >&2
    exit 1
fi

# Validate JSON array
if ! echo "$EXECUTION_STEPS" | jq -e 'type == "array"' > /dev/null 2>&1; then
    echo '{"success":false,"error":"executionSteps must be a valid JSON array"}' >&2
    exit 1
fi

# Create directory structure
TASK_DIR=".task-reports/${TASK_ID}"
mkdir -p "$TASK_DIR/reports" "$TASK_DIR/signals"

NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Create metadata file with full structure
METADATA_FILE="${TASK_DIR}/metadata.json"
cat > "$METADATA_FILE" <<EOF
{
  "taskId": "$TASK_ID",
  "executionSteps": $EXECUTION_STEPS,
  "currentStepIndex": 0,
  "startedAt": "$NOW",
  "savedAt": "$NOW"
}
EOF

echo "{\"success\":true,\"path\":\"$METADATA_FILE\"}"
