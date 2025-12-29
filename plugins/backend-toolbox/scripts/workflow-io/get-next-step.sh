#!/usr/bin/env bash
# Get the next step for a task
# Usage: get-next-step.sh <taskId>
# Returns: stepNumber, totalSteps, step (current step to execute), complete flag

set -e

# Source shared base directory helper
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_base-dir.sh"

TASK_ID="$1"

if [[ -z "$TASK_ID" ]]; then
    echo '{"success":false,"error":"Missing required parameter: taskId"}' >&2
    exit 1
fi

METADATA_FILE="${TASK_REPORTS_BASE}/${TASK_ID}/metadata.json"

if [[ ! -f "$METADATA_FILE" ]]; then
    echo "{\"success\":false,\"error\":\"Metadata not found for taskId: $TASK_ID\"}" >&2
    exit 1
fi

# Read metadata
METADATA=$(cat "$METADATA_FILE")

# Extract fields using jq
CURRENT_STEP_INDEX=$(echo "$METADATA" | jq -r '.currentStepIndex')
EXECUTION_STEPS=$(echo "$METADATA" | jq -c '.executionSteps')
TOTAL_STEPS=$(echo "$METADATA" | jq '.executionSteps | length')
COMPLETED_AT=$(echo "$METADATA" | jq -r '.completedAt // empty')

# Check if complete
if [[ -n "$COMPLETED_AT" ]]; then
    echo "{\"success\":true,\"taskId\":\"$TASK_ID\",\"stepNumber\":$((CURRENT_STEP_INDEX + 1)),\"totalSteps\":$TOTAL_STEPS,\"complete\":true}"
    exit 0
fi

# Get current step (can be a string or array for parallel steps)
CURRENT_STEP=$(echo "$EXECUTION_STEPS" | jq -c ".[$CURRENT_STEP_INDEX]")

echo "{\"success\":true,\"taskId\":\"$TASK_ID\",\"stepNumber\":$((CURRENT_STEP_INDEX + 1)),\"totalSteps\":$TOTAL_STEPS,\"step\":$CURRENT_STEP,\"complete\":false}"
