#!/usr/bin/env bash
# Get task metadata
# Usage: get-metadata.sh <taskId>

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
    echo "{\"success\":false,\"error\":\"Metadata not found for task: $TASK_ID\"}" >&2
    exit 1
fi

cat "$METADATA_FILE"
