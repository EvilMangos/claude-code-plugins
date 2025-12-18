---
description: Make DevOps changes (CI/CD, Docker, K8s, Terraform) with planning and review workflow
argument-hint: [ change-description ]
allowed-tools: Read, Edit, Write, Grep, Glob, Task
---

You are orchestrating a **DevOps change workflow** for this repository.

The user request is:

> $ARGUMENTS

You MUST follow this workflow strictly and delegate to the named subagents at each step.
Do not do a subagent's work in the main agent.

Required subagents:

- plan-creator
- devops-specialist
- acceptance-reviewer

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

## Workflow

### 1) Clarify & high-level understanding (main agent)

- Restate the change request in your own words.
- Identify affected configuration files and infrastructure components.
- If anything is ambiguous, list assumptions explicitly.
- Derive a list of **expected outcomes** (what should change, what should remain stable).

### 2) Planning (delegate to `plan-creator`)

- Invoke `plan-creator` to:
    - Explore the relevant configuration files and infrastructure code.
    - Produce a step-by-step implementation plan.
    - Map each change to concrete files and locations.
    - Highlight risks, dependencies, and open questions.
- Adopt or refine the plan before proceeding.
- Ensure the plan covers:
    - **What files to modify** (Dockerfiles, workflows, manifests, etc.)
    - **What to add/change/remove** in each file
    - **Verification steps** (how to validate the changes work)

### 3) Apply modifications (delegate to `devops-specialist`)

- Pass to `devops-specialist`:
    - The approved plan
    - The expected outcomes list
    - The affected file paths
- The `devops-specialist` must:
    - Implement changes following the plan
    - Apply DevOps best practices (security, reproducibility, minimal changes)
    - Provide verification commands to test changes locally
- After implementation, summarize:
    - Files changed and what was modified
    - Any deviations from the plan and why
    - Suggested verification commands

### 4) Quality & security review (delegate to `devops-specialist`)

- Re-invoke `devops-specialist` with explicit review instructions:
    - Review the changes made in Step 3 for quality and security issues
    - Check against DevOps best practices checklists:
        - Docker: base image pinning, non-root user, no secrets in layers, health checks
        - CI/CD: pinned action versions, minimal permissions, proper secret handling
        - Kubernetes: resource limits, security context, probes configured
        - Terraform: no hardcoded secrets, proper state handling, consistent naming
    - Identify any issues or improvements needed
- The review must return a verdict: **PASS / PARTIAL / FAIL**
    - PASS: Changes meet quality and security standards
    - PARTIAL: Minor issues that should be addressed
    - FAIL: Critical issues that must be fixed

**⛔ MANDATORY GATE - NO EXCEPTIONS, NO RATIONALIZATION:**

You MUST NOT proceed to Step 5 unless verdict == PASS.

- Do NOT rationalize skipping this gate ("issues are minor", "config is acceptable", etc.)
- Do NOT use your own judgment to override this gate
- PARTIAL means the loop MUST execute - no exceptions

```
LOOP while verdict != PASS (max 5 iterations):
  IF verdict is PARTIAL or FAIL:
    1. Invoke devops-specialist to fix the identified issues
    2. Re-invoke code-reviewer for quality review
    3. Check verdict again
  END IF
END LOOP
```

**HARD STOP: Only proceed to Step 5 after verdict == PASS.**

### 5) Acceptance review (delegate to `acceptance-reviewer`)

- Provide `acceptance-reviewer`:
    - The original request (`$ARGUMENTS` and clarifications)
    - The plan from `plan-creator`
    - A summary of changes made by `devops-specialist`
    - The quality review verdict and any notes
- Have the subagent:
    - Check whether all requirements from the original request are met
    - Verify expected outcomes are achieved
    - Produce a verdict: **PASS / PARTIAL / FAIL** with a requirements checklist

**⛔ MANDATORY GATE - NO EXCEPTIONS, NO RATIONALIZATION:**

You MUST NOT complete the workflow unless verdict == PASS.

- Do NOT rationalize skipping this gate ("mostly meets requirements", "good enough", etc.)
- Do NOT use your own judgment to override this gate
- PARTIAL means the loop MUST execute - no exceptions

```
LOOP while verdict != PASS (max 5 iterations):
  IF verdict is PARTIAL or FAIL:
    1. Invoke devops-specialist to address gaps
    2. IF changes are significant: Re-invoke code-reviewer for quality review (Step 4)
    3. Re-invoke acceptance-reviewer
    4. Check verdict again
  END IF
END LOOP
```

**HARD STOP: Workflow completes only after verdict == PASS.**

## Non-negotiable constraints

- Do not modify application code, only infrastructure/deployment configuration.
- Follow security best practices: no hardcoded secrets, minimal permissions, pinned versions.
- Prefer minimal changes that achieve the goal without unnecessary refactoring.
- Provide verification commands for every change so users can test locally.
- Do not proceed to acceptance review until quality review passes.
