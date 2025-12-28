---
description: Make DevOps changes (CI/CD, Docker, K8s, Terraform) with planning and review workflow
argument-hint: [ change-description ]
allowed-tools: Read, Edit, Write, Grep, Glob, Task, Skill, MCP
---

# DevOps Change Workflow (Background Agent Orchestration)

You are orchestrating a **DevOps change workflow** for this repository.

The user request is:

> $ARGUMENTS

## Architecture: Workflow

This workflow drives all decisions:

1. **Orchestrator initializes task** with metadata
2. **The workflow determines the next step** based on current state
3. **Orchestrator executes the step** returned by the workflow
4. **Agent saves report and signal**
5. **Orchestrator queries for next step** - repeat until complete

**The orchestrator NEVER decides which step to run next. The workflow makes all routing decisions.**

## Workflow Scripts

All orchestrator operations use scripts in `${CLAUDE_PLUGIN_ROOT}/scripts/workflow-io/`:

| Operation | Script | Usage |
|-----------|--------|-------|
| Create metadata | `create-metadata.sh <taskId> '<stepsJson>'` | Initialize task with execution steps |
| Get next step | `get-next-step.sh <taskId>` | Returns current step to execute |
| Wait for signal | `wait-signal.sh <taskId> <signalType(s)>` | Waits for signal(s), advances workflow |
| Get report | `get-report.sh <taskId> <reportType>` | Retrieves full report content |

Notes:
- `stepsJson` is a JSON array, arrays within represent parallel steps: `'["plan",["perf","security"],"impl"]'`
- For parallel signals, use comma-separated types: `wait-signal.sh $TASK_ID "performance,security"`
- Scripts output JSON to stdout; parse with jq

## Task ID Generation

Before starting, generate a unique task ID for this workflow:

```
TASK_ID = devops-change-{slug}-{timestamp}
```

Where:
- `slug`: URL-safe version of change description (lowercase, hyphens, max 30 chars)
  - Example: "Add GitHub Actions CI" → `add-github-actions-ci`
  - Example: "Update Docker build for ARM" → `update-docker-build-for-arm`
- `timestamp`: Unix timestamp in seconds (e.g., `1702834567`)

Example: `devops-change-add-github-actions-ci-1702834567`

## Scope

This workflow handles infrastructure and deployment configuration changes:

- **CI/CD pipelines**: GitHub Actions, GitLab CI, Jenkins, Azure Pipelines
- **Containerization**: Dockerfiles, docker-compose, .dockerignore
- **Orchestration**: Kubernetes manifests, Helm charts, Skaffold
- **Infrastructure as Code**: Terraform, Pulumi, CloudFormation

This workflow does NOT handle:

- Application/business logic code (use `/develop-feature`)
- Test files (use `/develop-feature`)
- Database migrations (use `/develop-feature`)

## Orchestrator Loop

After initialization, the orchestrator runs this loop:

```
LOOP:
  1. Get next step (returns: stepNumber, totalSteps, step, complete)
     - step can be a string ("plan") or array for parallel (["performance", "security"])

  2. IF complete == true:
     - Output final signal summary to user
     - EXIT LOOP

  3. IF step is an array (parallel execution):
     - Launch ALL agents in parallel (single message, multiple Task tool calls)
     - Wait for all signals (comma-separated types)

  4. ELSE (step is a string):
     - Launch the single agent for the returned step
     - Wait for signal

  5. GOTO 1
END LOOP
```

**Critical Rules:**

1. **The orchestrator does NOT interpret signal status to decide next step. It always queries the workflow.**

2. **Always execute the step returned, even if that step was already executed before.**
   - The workflow may return the same step multiple times (e.g., `implementation` after a failed `acceptance`)
   - This is intentional: the workflow handles retry logic and gate failures internally
   - Do NOT skip a step because "it was already done"
   - Do NOT question why a repeated step is being requested
   - Simply execute whatever step is returned, every time

3. **NEVER use TaskOutput to retrieve background agent results.**
   - Background agents communicate ONLY via signals and reports
   - Using TaskOutput pulls verbose agent output (tool calls, file reads, etc.) into the main context
   - This wastes context window and defeats the purpose of background execution
   - If you need agent results: use get-report script, NOT TaskOutput
   - The signal summary provides enough info for the orchestrator to proceed

## Agent Output Instructions

**Always include these instructions in every agent prompt:**
```
## Workflow Context
TASK_ID: {TASK_ID}

## Output
1. Save your FULL report:
   - taskId: {TASK_ID}
   - reportType: {report-type}  (e.g., "requirements", "plan", "implementation")
   - content: <your full report content>

2. Save your signal:
   - taskId: {TASK_ID}
   - signalType: {report-type}  (same as reportType)
   - content:
     - status: "passed" or "failed"
     - summary: {one sentence describing outcome}

   Status mapping:
   - "passed" = completed successfully, gate passed, no issues found
   - "failed" = needs iteration, has issues to resolve, or error occurred
     (include details in summary: "PARTIAL: ...", "ISSUES: N", "ERROR: ...")
```

---

## Step Definitions

The following steps can be returned. Execute the corresponding agent when the step is returned.

### initialize

Create task metadata:
- taskId: {TASK_ID}
- executionSteps: `["requirements", "codebase-analysis", "plan", "implementation", "code-review", "acceptance", "finalize"]`

### Step 1: requirements (business-analyst)

```
subagent_type: business-analyst
run_in_background: false
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Analyze the DevOps change request and create specific requirements:
  - Restate the change in your own words
  - Identify affected configuration files and infrastructure components
  - List ALL ambiguous points, unclear terms, or missing details
  - If ambiguities exist: ask ALL questions using AskUserQuestion tool
  - Review answers; if unclear or introduce new ambiguities, ask follow-ups
  - Derive expected outcomes (OUTCOME-1, OUTCOME-2, etc.)

  ## Change Request
  $ARGUMENTS

  ## Output
  1. Save FULL report:
     - taskId: {TASK_ID}
     - reportType: "requirements"
     - content: Include Change Understanding, Affected Components, Clarifications, Expected Outcomes (OUTCOME-1, OUTCOME-2, etc.)
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "requirements"
     - content: { status: "passed", summary: "Requirements analysis complete with N outcomes" }
```

### Step 2: codebase-analysis (codebase-analyzer)

```
subagent_type: codebase-analyzer
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Analyze the codebase to identify existing DevOps practices, patterns, and conventions.
  This analysis will guide implementation to ensure consistency.

  Focus on:
  - Existing CI/CD pipeline structure
  - Containerization patterns (Dockerfile conventions, compose structure)
  - Infrastructure as Code patterns
  - Secret management approaches
  - Environment configuration patterns
  - Deployment conventions

  ## Input Reports
  Retrieve (taskId={TASK_ID}):
  - reportType: "requirements" (to understand what areas are relevant)

  ## Output
  1. Save FULL report:
     - taskId: {TASK_ID}
     - reportType: "codebase-analysis"
     - content: <your codebase analysis report>
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "codebase-analysis"
     - content: { status: "passed", summary: "Codebase analysis complete" }
```

### Step 3: plan (plan-creator)

```
subagent_type: plan-creator
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Create implementation plan for the DevOps change.
  Use the codebase analysis to ensure the plan follows existing patterns.

  The plan must cover:
  - What files to modify (Dockerfiles, workflows, manifests, etc.)
  - What to add/change/remove in each file
  - Verification steps (how to validate the changes work)
  - Risk assessment and dependencies

  ## Input Reports
  Retrieve (taskId={TASK_ID}):
  - reportType: "requirements"
  - reportType: "codebase-analysis"

  ## Output
  1. Save FULL report:
     - taskId: {TASK_ID}
     - reportType: "plan"
     - content: <your implementation plan>
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "plan"
     - content: { status: "passed", summary: "Implementation plan created" }
```

### Step 4: implementation (devops-specialist)

```
subagent_type: devops-specialist
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Implement the DevOps changes following the plan.
  - Apply DevOps best practices (security, reproducibility, minimal changes)
  - Follow patterns identified in codebase-analysis
  - Provide verification commands to test changes locally

  ## Input Reports
  Retrieve (taskId={TASK_ID}):
  Required:
  - reportType: "requirements"
  - reportType: "codebase-analysis"
  - reportType: "plan"
  Optional (retrieve if available - contains feedback requiring fixes):
  - reportType: "code-review"
  - reportType: "acceptance"

  ## Output
  1. Save FULL report:
     - taskId: {TASK_ID}
     - reportType: "implementation"
     - content: Include files changed, what was modified, verification commands
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "implementation"
     - content: { status: "passed", summary: "Implementation complete" }
```

### Step 5: code-review (devops-specialist as reviewer)

```
subagent_type: devops-specialist
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Review the DevOps changes for quality and security issues.
  Check against DevOps best practices checklists:
  - Docker: base image pinning, non-root user, no secrets in layers, health checks
  - CI/CD: pinned action versions, minimal permissions, proper secret handling
  - Kubernetes: resource limits, security context, probes configured
  - Terraform: no hardcoded secrets, proper state handling, consistent naming

  Apply your loaded skill (`devops-infrastructure-security`).

  Return verdict in signal:
  - status: "passed" = no issues found
  - status: "failed" = issues found (include "ISSUES: N" in summary)

  ## Input Reports
  Retrieve (taskId={TASK_ID}):
  - reportType: "codebase-analysis"
  - reportType: "plan"
  - reportType: "implementation"

  ## Output
  1. Save FULL report:
     - taskId: {TASK_ID}
     - reportType: "code-review"
     - content: <your code review report with verdict>
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "code-review"
     - content: { status: "passed" or "failed", summary: "..." }
```

### Step 6: acceptance (acceptance-reviewer)

```
subagent_type: acceptance-reviewer
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Verify all expected outcomes are met:
  - Check each OUTCOME-N against implementation
  - Verify the original change request is satisfied
  - Identify any functional gaps

  Return verdict in signal:
  - status: "passed" = all outcomes met
  - status: "failed" = gaps found (include "PARTIAL: ..." in summary)

  ## Input Reports
  Retrieve (taskId={TASK_ID}):
  - reportType: "requirements"
  - reportType: "plan"
  - reportType: "implementation"
  - reportType: "code-review"

  ## Output
  1. Save FULL report:
     - taskId: {TASK_ID}
     - reportType: "acceptance"
     - content: <your acceptance review report with verdict>
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "acceptance"
     - content: { status: "passed" or "failed", summary: "..." }
```

### Step 7: finalize (workflow-finalizer)

```
subagent_type: workflow-finalizer
run_in_background: true
prompt: |
  ## Workflow Context
  TASK_ID: {TASK_ID}

  ## Task
  Generate an executive summary of the completed DevOps change workflow.

  Read all available reports for this task and synthesize:
  - Overall outcome (success/partial/failed)
  - Key changes made to infrastructure/deployment
  - Verification commands for testing
  - Open items/follow-ups (if any)
  - Files changed

  Keep the summary concise and focused on outcomes.

  ## Output
  1. Save FULL report:
     - taskId: {TASK_ID}
     - reportType: "finalize"
     - content: <your executive summary>
  2. Save signal:
     - taskId: {TASK_ID}
     - signalType: "finalize"
     - content: { status: "passed", summary: "DevOps change complete: <one-sentence outcome>" }
```

After the finalize signal is received, the orchestrator outputs the signal summary to the user and exits.

---

## Non-negotiable constraints

- Do not modify application code, only infrastructure/deployment configuration.
- Follow security best practices: no hardcoded secrets, minimal permissions, pinned versions.
- Prefer minimal changes that achieve the goal without unnecessary refactoring.
- Provide verification commands for every change so users can test locally.
