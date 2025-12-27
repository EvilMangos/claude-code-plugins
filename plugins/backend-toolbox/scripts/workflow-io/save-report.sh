#!/usr/bin/env bash
# Save a workflow report to file
# Usage: save-report.sh <taskId> <reportType> <content>
# Or pipe content: echo "content" | save-report.sh <taskId> <reportType>

set -e

TASK_ID="$1"
REPORT_TYPE="$2"
CONTENT="$3"

if [[ -z "$TASK_ID" || -z "$REPORT_TYPE" ]]; then
    echo '{"success":false,"error":"Missing required parameters: taskId and reportType"}' >&2
    exit 1
fi

# Valid report types
VALID_TYPES="requirements codebase-analysis plan tests-design tests-review implementation stabilization acceptance performance security refactoring code-review documentation finalize"
if [[ ! " $VALID_TYPES " =~ " $REPORT_TYPE " ]]; then
    echo "{\"success\":false,\"error\":\"Invalid reportType: $REPORT_TYPE\"}" >&2
    exit 1
fi

# If content not provided as arg, read from stdin
if [[ -z "$CONTENT" ]]; then
    CONTENT=$(cat)
fi

# Create directory structure
REPORTS_DIR=".task-reports/${TASK_ID}/reports"
mkdir -p "$REPORTS_DIR"

# Save report
REPORT_FILE="${REPORTS_DIR}/${REPORT_TYPE}.md"
echo "$CONTENT" > "$REPORT_FILE"

echo "{\"success\":true,\"path\":\"$REPORT_FILE\"}"
