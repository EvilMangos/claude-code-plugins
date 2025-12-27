#!/usr/bin/env bash
# Get a workflow report from file
# Usage: get-report.sh <taskId> <reportType>

set -e

TASK_ID="$1"
REPORT_TYPE="$2"

if [[ -z "$TASK_ID" || -z "$REPORT_TYPE" ]]; then
    echo '{"success":false,"error":"Missing required parameters: taskId and reportType"}' >&2
    exit 1
fi

# Valid report types
VALID_TYPES="requirements codebase-analysis plan tests-design tests-review implementation stabilization acceptance performance security refactoring code-review documentation"
if [[ ! " $VALID_TYPES " =~ " $REPORT_TYPE " ]]; then
    echo "{\"success\":false,\"error\":\"Invalid reportType: $REPORT_TYPE\"}" >&2
    exit 1
fi

REPORT_FILE=".task-reports/${TASK_ID}/reports/${REPORT_TYPE}.md"

if [[ ! -f "$REPORT_FILE" ]]; then
    echo "{\"success\":false,\"error\":\"Report not found: $REPORT_FILE\"}" >&2
    exit 1
fi

# Output the report content
cat "$REPORT_FILE"
