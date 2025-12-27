#!/usr/bin/env bash
# Wait for workflow signal(s) to exist and handle step progression
# Usage: wait-signal.sh <taskId> <signalType(s)> [timeout_seconds]
# signalType(s) can be a single type or comma-separated for parallel steps: "performance,security"
# Polls until ALL signal files exist or timeout (default: 300s)
# On success: increments step if all passed, decrements if any failed

set -e

TASK_ID="$1"
SIGNAL_TYPES_INPUT="$2"
TIMEOUT="${3:-300}"

if [[ -z "$TASK_ID" || -z "$SIGNAL_TYPES_INPUT" ]]; then
    echo '{"success":false,"error":"Missing required parameters: taskId and signalType"}' >&2
    exit 1
fi

# Valid signal types
VALID_TYPES="requirements codebase-analysis plan tests-design tests-review implementation stabilization acceptance performance security refactoring code-review documentation finalize"

# Parse signal types (comma-separated for parallel)
IFS=',' read -ra SIGNAL_TYPES <<< "$SIGNAL_TYPES_INPUT"

# Validate all signal types
for TYPE in "${SIGNAL_TYPES[@]}"; do
    if [[ ! " $VALID_TYPES " =~ " $TYPE " ]]; then
        echo "{\"success\":false,\"error\":\"Invalid signalType: $TYPE\"}" >&2
        exit 1
    fi
done

SIGNALS_DIR=".task-reports/${TASK_ID}/signals"
METADATA_FILE=".task-reports/${TASK_ID}/metadata.json"
POLL_INTERVAL=2
START_TIME=$(date +%s)

# Wait for ALL signals
while true; do
    ELAPSED=$(($(date +%s) - START_TIME))

    if [[ $ELAPSED -ge $TIMEOUT ]]; then
        # Find missing signals
        MISSING=""
        for TYPE in "${SIGNAL_TYPES[@]}"; do
            if [[ ! -f "${SIGNALS_DIR}/${TYPE}.json" ]]; then
                MISSING="${MISSING}${TYPE},"
            fi
        done
        MISSING="${MISSING%,}"
        echo "{\"success\":false,\"error\":\"Timeout after ${TIMEOUT}s waiting for signals [$MISSING] (taskId: $TASK_ID)\",\"waitedMs\":$((ELAPSED * 1000))}" >&2
        exit 1
    fi

    # Check if all signals exist
    ALL_FOUND=true
    for TYPE in "${SIGNAL_TYPES[@]}"; do
        if [[ ! -f "${SIGNALS_DIR}/${TYPE}.json" ]]; then
            ALL_FOUND=false
            break
        fi
    done

    if $ALL_FOUND; then
        break
    fi

    sleep $POLL_INTERVAL
done

ELAPSED=$(($(date +%s) - START_TIME))

# Collect all signal contents and check statuses
CONTENTS="["
ALL_PASSED=true
FIRST=true

for TYPE in "${SIGNAL_TYPES[@]}"; do
    SIGNAL_FILE="${SIGNALS_DIR}/${TYPE}.json"
    CONTENT=$(cat "$SIGNAL_FILE")
    STATUS=$(echo "$CONTENT" | jq -r '.status')

    if [[ "$STATUS" != "passed" ]]; then
        ALL_PASSED=false
    fi

    if $FIRST; then
        CONTENTS="${CONTENTS}${CONTENT}"
        FIRST=false
    else
        CONTENTS="${CONTENTS},${CONTENT}"
    fi
done

CONTENTS="${CONTENTS}]"

# Update metadata step progression
if [[ -f "$METADATA_FILE" ]]; then
    METADATA=$(cat "$METADATA_FILE")
    CURRENT_INDEX=$(echo "$METADATA" | jq -r '.currentStepIndex')
    TOTAL_STEPS=$(echo "$METADATA" | jq '.executionSteps | length')
    NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)

    if $ALL_PASSED; then
        # Increment step
        MAX_INDEX=$((TOTAL_STEPS - 1))
        if [[ $CURRENT_INDEX -ge $MAX_INDEX ]]; then
            # At last step - mark as complete
            echo "$METADATA" | jq --arg now "$NOW" '.completedAt = $now | .savedAt = $now' > "$METADATA_FILE"
        else
            # Move to next step
            NEW_INDEX=$((CURRENT_INDEX + 1))
            echo "$METADATA" | jq --arg now "$NOW" --argjson idx "$NEW_INDEX" '.currentStepIndex = $idx | .savedAt = $now' > "$METADATA_FILE"
        fi
    else
        # Decrement step (go back to retry)
        if [[ $CURRENT_INDEX -gt 0 ]]; then
            NEW_INDEX=$((CURRENT_INDEX - 1))
            echo "$METADATA" | jq --arg now "$NOW" --argjson idx "$NEW_INDEX" '.currentStepIndex = $idx | .savedAt = $now' > "$METADATA_FILE"
        fi
    fi
fi

# Return result
echo "{\"success\":true,\"content\":$CONTENTS,\"waitedMs\":$((ELAPSED * 1000))}"
