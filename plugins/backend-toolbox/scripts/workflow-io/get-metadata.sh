#!/usr/bin/env bash
# Get task metadata
# Usage: get-metadata.sh <taskId>

set -e

TASK_ID="$1"

if [[ -z "$TASK_ID" ]]; then
    echo '{"success":false,"error":"Missing required parameter: taskId"}' >&2
    exit 1
fi

METADATA_FILE=".task-reports/${TASK_ID}/metadata.json"

if [[ ! -f "$METADATA_FILE" ]]; then
    echo "{\"success\":false,\"error\":\"Metadata not found for task: $TASK_ID\"}" >&2
    exit 1
fi

cat "$METADATA_FILE"
