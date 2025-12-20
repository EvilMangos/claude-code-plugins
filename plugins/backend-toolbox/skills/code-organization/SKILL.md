---
name: code-organization
description: This skill should be used when the user asks about code organization, file structure, granularity, module boundaries, "how to split this file", "file is too large", "too many things in one file", "folder structure", "project structure", "organize code", "modular code", "break down this module", "single file has too much", "where should this code live", or needs guidance on file size limits, when to split vs merge code, and folder/package organization patterns.
version: 0.1.0
---

# Code Organization

Comprehensive guidance on code granularity, file structure, module boundaries, and when to split code. Use this skill when organizing code or deciding how to structure files and folders.

## Sizing Guidelines

### File Size Thresholds

| Element | Threshold | Action When Exceeded |
|---------|-----------|----------------------|
| **File** | > 300 lines | Consider splitting into focused modules |
| **File** | > 500 lines | Must split - too many responsibilities |
| **Class/Type** | > 200-300 lines | Extract sub-components or helper classes |
| **Function/Method** | > 30 lines | Extract helper functions |
| **Function/Method** | > 50 lines | Must refactor - too complex |
| **Parameters** | > 3-4 params | Consider parameter object |
| **Imports** | > 15-20 imports | File likely has too many responsibilities |

### File Responsibility Indicators

A file should be split when ANY of these apply:

- [ ] File does more than one "thing" (use the "and" test - if you need "and" to describe it, split it)
- [ ] Changes to one feature require modifying unrelated code in the same file
- [ ] Multiple developers frequently conflict on the same file
- [ ] You struggle to name the file without using generic terms ("utils", "helpers", "common")
- [ ] The file has multiple distinct "sections" separated by comments
- [ ] Test file for this module is excessively large or hard to organize

## Granularity Decision Framework

### When to Split

**Split immediately when:**

1. **Size exceeded** - File > 300 lines or function > 30 lines
2. **Multiple responsibilities** - File serves different purposes or domains
3. **Merge conflicts** - Team members often conflict on the same file
4. **Test complexity** - Testing requires extensive mocking of unrelated parts
5. **Naming struggle** - Can't name without "and", "utils", "helpers", "common"

**Split proactively when:**

1. **Feature boundaries** - Different features share a file
2. **Layer mixing** - UI, business logic, and data access in one file
3. **Reusability blocked** - Can't reuse part of file without importing unrelated code
4. **Cognitive load** - Takes time to find relevant code in the file

### When NOT to Split

**Keep together when:**

1. **High cohesion** - All code in file changes together for same reasons
2. **Single concept** - File represents one complete concept (entity, service, component)
3. **Premature abstraction** - Splitting would create artificial boundaries
4. **Size acceptable** - File is under thresholds and well-organized
5. **No reuse need** - Parts won't be used independently

### Decision Tree

```
Is file > 300 lines?
├─ YES → Split by responsibility
└─ NO → Can you describe file purpose without "and"?
         ├─ NO → Split by responsibility
         └─ YES → Do unrelated things change together?
                  ├─ YES → Split by change reason
                  └─ NO → Keep as-is, file is well-organized
```

## Module Boundary Principles

### One Thing Per File

Each file should have a **single, clear purpose**:

| Good (Focused) | Bad (Mixed) |
|----------------|-------------|
| `user-repository.ts` | `user-stuff.ts` |
| `order-validator.ts` | `order-helpers.ts` |
| `payment-gateway.ts` | `payment-utils.ts` |
| `email-template.ts` | `common.ts` |

### Naming Rules

**File names should:**

- Describe what the file DOES, not what it CONTAINS
- Be specific enough to predict contents
- Avoid generic suffixes: `-utils`, `-helpers`, `-common`, `-misc`
- Match the primary export name

**Red flag names (require splitting):**

- `utils.ts`, `helpers.ts`, `common.ts`, `misc.ts`
- `*-stuff.ts`, `*-things.ts`
- `index.ts` with actual logic (not just re-exports)
- Names with "and" or multiple concepts

### Cohesion Check

Ask these questions:

1. **Does every function use the same data?** If not, split by data ownership
2. **Do all exports serve the same consumer?** If not, split by consumer
3. **Would you test all parts together?** If not, split by testability boundary
4. **Does everything change for the same reason?** If not, split by change reason

## Folder Structure Patterns

### Pattern 1: Feature-Based (Recommended for most apps)

Organize by **what the code does** (business capability):

```
src/
├── features/
│   ├── auth/
│   │   ├── login.ts
│   │   ├── logout.ts
│   │   ├── password-reset.ts
│   │   └── auth.test.ts
│   ├── orders/
│   │   ├── create-order.ts
│   │   ├── order-repository.ts
│   │   ├── order-validator.ts
│   │   └── orders.test.ts
│   └── users/
│       ├── user-profile.ts
│       ├── user-repository.ts
│       └── users.test.ts
├── shared/
│   ├── database/
│   └── http/
└── main.ts
```

**Best for:** Most applications, teams organized by feature

### Pattern 2: Layer-Based

Organize by **technical layer**:

```
src/
├── controllers/
│   ├── order-controller.ts
│   └── user-controller.ts
├── services/
│   ├── order-service.ts
│   └── user-service.ts
├── repositories/
│   ├── order-repository.ts
│   └── user-repository.ts
├── models/
│   ├── order.ts
│   └── user.ts
└── main.ts
```

**Best for:** Small apps, strict architectural enforcement

### Pattern 3: Hexagonal/Ports-Adapters

Organize by **dependency direction**:

```
src/
├── domain/                    # Core business logic (no dependencies)
│   ├── order/
│   │   ├── order.ts           # Entity
│   │   ├── order-service.ts   # Domain service
│   │   └── order-repository.ts # Port (interface)
│   └── user/
├── application/               # Use cases, orchestration
│   ├── create-order.ts
│   └── register-user.ts
├── infrastructure/            # External adapters
│   ├── persistence/
│   │   ├── postgres-order-repository.ts
│   │   └── postgres-user-repository.ts
│   ├── http/
│   │   └── express-server.ts
│   └── messaging/
└── main.ts                    # Composition root
```

**Best for:** Complex domains, long-lived systems, DDD projects

### Pattern 4: Module-Based (Monorepo-friendly)

Organize as **independent packages**:

```
packages/
├── core/                      # Shared types, utilities
│   ├── src/
│   └── package.json
├── orders/                    # Order domain
│   ├── src/
│   │   ├── domain/
│   │   ├── infrastructure/
│   │   └── index.ts
│   └── package.json
├── users/                     # User domain
│   ├── src/
│   └── package.json
└── api/                       # HTTP API
    ├── src/
    └── package.json
```

**Best for:** Large systems, multiple teams, shared code

## What Goes Where

### Contracts/Interfaces Layer

```
contracts/
├── repositories/
│   ├── order-repository.ts    # Interface OrderRepository
│   └── user-repository.ts
├── services/
│   └── email-service.ts       # Interface EmailService
└── index.ts                   # Re-exports all contracts
```

**Rule:** Interfaces live in contracts layer, NOT with consumers or providers.

### Shared Code

**Should be in shared/ when:**

- Used by 3+ features (Rule of Three)
- Truly generic (not feature-specific)
- Stable API (rarely changes)

**Should NOT be in shared/ when:**

- Used by only 1-2 features (keep with feature)
- Feature-specific logic
- Frequently changing

### Test Organization

| Pattern | Structure |
|---------|-----------|
| **Colocated** | `feature/user.ts` + `feature/user.test.ts` |
| **Mirror** | `src/feature/user.ts` + `tests/feature/user.test.ts` |
| **Type-based** | `tests/unit/...` + `tests/integration/...` |

**Recommendation:** Colocated for unit tests, separate folder for integration/e2e.

## Splitting Strategies

### Strategy 1: By Entity/Concept

Split one "god file" into focused files per entity:

```
Before: user-management.ts (500 lines)

After:
├── user.ts              # User entity
├── user-repository.ts   # Data access
├── user-validator.ts    # Validation logic
├── user-service.ts      # Business logic
└── user-controller.ts   # HTTP handlers
```

### Strategy 2: By Operation

Split by what operations the code performs:

```
Before: order-service.ts (400 lines doing CRUD + validation + notifications)

After:
├── create-order.ts      # Create operation
├── update-order.ts      # Update operation
├── order-validator.ts   # Validation
└── order-notifier.ts    # Notifications
```

### Strategy 3: By Consumer

Split by who uses the code:

```
Before: utils.ts (300 lines used by everything)

After:
├── string-utils.ts      # Used by formatters
├── date-utils.ts        # Used by scheduling
├── validation-utils.ts  # Used by validators
└── http-utils.ts        # Used by API layer
```

### Strategy 4: By Abstraction Level

Split by how "high-level" the code is:

```
Before: payment.ts (mixing orchestration with details)

After:
├── payment-service.ts       # High-level orchestration
├── payment-gateway.ts       # External integration
├── payment-calculator.ts    # Business rules
└── payment-repository.ts    # Data access
```

## Anti-Patterns

### Files to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| `utils.ts` | Dumping ground, low cohesion | Split by domain or consumer |
| `helpers.ts` | Vague purpose | Name by what it helps with |
| `common.ts` | Everything ends up here | Extract to feature modules |
| `constants.ts` (large) | Mix of unrelated constants | Colocate with usage |
| `types.ts` (large) | Mix of unrelated types | Colocate with implementation |
| `index.ts` with logic | Hidden complexity | Only re-exports in index |

### Structural Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| **God Module** | One file does everything | Split by responsibility |
| **Feature Envy** | File mostly uses another file's data | Move code to data owner |
| **Circular Dependencies** | A imports B, B imports A | Extract shared to third module |
| **Deep Nesting** | `src/a/b/c/d/e/f/file.ts` | Flatten, max 3-4 levels |
| **Flat Structure** | 50 files in one folder | Group by feature/layer |

## Quick Reference Card

### File Size Limits

- **File:** 300 lines soft limit, 500 hard limit
- **Function:** 30 lines soft limit, 50 hard limit
- **Class:** 200-300 lines

### Split Triggers

- Size exceeded
- Multiple responsibilities
- Can't name without "and"
- Different change reasons
- Merge conflicts

### Keep Together When

- High cohesion
- Single concept
- Under size limits
- Same change reason

### Folder Depth

- Max 3-4 levels deep
- Feature > Layer for most apps
- Colocate related code

## Additional Resources

For detailed guidance on specific aspects:

- **`references/granularity-decisions.md`** - Extended decision trees and examples
- **`references/folder-patterns.md`** - Detailed folder structure patterns by project type

### Related Skills

- **design-assessment** - Identify code smells that indicate poor organization
- **design-patterns** - Patterns for structuring code (SRP, DIP, layers)
- **refactoring-patterns** - Mechanics for reorganizing code (Extract, Move)
- **code-review-checklist** - Verify organization quality during review
