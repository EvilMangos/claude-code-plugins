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
  reportType: requirements
```

### Step 2: codebase-analysis (codebase-analyzer)

```
subagent_type: codebase-analyzer
run_in_background: true
prompt: |
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
  - requirements

  ## Output
  reportType: codebase-analysis
```

### Step 3: plan (plan-creator)

```
subagent_type: plan-creator
run_in_background: true
prompt: |
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
  - requirements
  - codebase-analysis

  ## Output
  reportType: plan
```

### Step 4: implementation (devops-specialist)

```
subagent_type: devops-specialist
run_in_background: true
prompt: |
  TASK_ID: {TASK_ID}

  ## Task
  Implement the DevOps changes following the plan.
  - Apply DevOps best practices (security, reproducibility, minimal changes)
  - Follow patterns identified in codebase-analysis
  - Provide verification commands to test changes locally

  ## Input Reports
  Required:
  - requirements
  - codebase-analysis
  - plan
  Optional (contains feedback requiring fixes):
  - code-review
  - acceptance

  ## Output
  reportType: implementation
```

### Step 5: code-review (devops-specialist as reviewer)

```
subagent_type: devops-specialist
run_in_background: true
prompt: |
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
  - codebase-analysis
  - plan
  - implementation

  ## Output
  reportType: code-review
```

### Step 6: acceptance (acceptance-reviewer)

```
subagent_type: acceptance-reviewer
run_in_background: true
prompt: |
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
  - requirements
  - plan
  - implementation
  - code-review

  ## Output
  reportType: acceptance
```

### Step 7: finalize (workflow-finalizer)

```
subagent_type: workflow-finalizer
run_in_background: true
prompt: |
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
  reportType: finalize
```

After the finalize signal is received, the orchestrator outputs the signal summary to the user and exits.

---

## Non-negotiable constraints

- Do not modify application code, only infrastructure/deployment configuration.
- Follow security best practices: no hardcoded secrets, minimal permissions, pinned versions.
- Prefer minimal changes that achieve the goal without unnecessary refactoring.
- Provide verification commands for every change so users can test locally.
