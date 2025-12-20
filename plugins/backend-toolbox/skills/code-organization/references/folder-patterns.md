# Folder Structure Patterns

Detailed folder organization patterns for different project types and team sizes.

## Pattern Selection Guide

| Project Type | Recommended Pattern | Why |
|--------------|---------------------|-----|
| **Small API** (< 10 endpoints) | Layer-Based | Simple, clear separation |
| **Medium App** (10-50 files) | Feature-Based | Scales with features |
| **Large System** (50+ files) | Hexagonal/DDD | Clear boundaries, testable |
| **Monorepo** (multiple apps) | Module-Based | Independent deployments |
| **Microservices** | Feature per Service | Natural service boundaries |

## Pattern 1: Layer-Based (Technical Layers)

Best for small-to-medium applications with clear technical boundaries.

### Structure

```
src/
├── controllers/           # HTTP request handlers
│   ├── user-controller.ts
│   ├── order-controller.ts
│   └── product-controller.ts
├── services/              # Business logic
│   ├── user-service.ts
│   ├── order-service.ts
│   └── product-service.ts
├── repositories/          # Data access
│   ├── user-repository.ts
│   ├── order-repository.ts
│   └── product-repository.ts
├── models/                # Data structures
│   ├── user.ts
│   ├── order.ts
│   └── product.ts
├── middleware/            # Express/Koa middleware
│   ├── auth.ts
│   ├── logging.ts
│   └── error-handler.ts
├── config/                # Configuration
│   ├── database.ts
│   └── server.ts
├── utils/                 # Shared utilities
│   └── validators.ts
└── main.ts
```

### Pros & Cons

| Pros | Cons |
|------|------|
| Simple mental model | Feature code scattered |
| Clear technical separation | Changes touch multiple folders |
| Easy for new developers | Doesn't scale past ~30 files |
| Matches common tutorials | Features hard to extract |

### When to Use

- Small APIs (< 10 endpoints)
- CRUD-heavy applications
- Solo developers or small teams
- Prototypes and MVPs

---

## Pattern 2: Feature-Based (Recommended Default)

Best for most applications. Groups code by business capability.

### Structure

```
src/
├── features/
│   ├── auth/
│   │   ├── login.ts
│   │   ├── logout.ts
│   │   ├── password-reset.ts
│   │   ├── auth-middleware.ts
│   │   ├── auth.test.ts
│   │   └── index.ts          # Public exports
│   ├── users/
│   │   ├── user.ts           # Entity
│   │   ├── user-service.ts   # Business logic
│   │   ├── user-repository.ts
│   │   ├── user-controller.ts
│   │   ├── user-validator.ts
│   │   ├── users.test.ts
│   │   └── index.ts
│   ├── orders/
│   │   ├── order.ts
│   │   ├── order-service.ts
│   │   ├── order-repository.ts
│   │   ├── order-controller.ts
│   │   ├── create-order.ts    # Use case
│   │   ├── cancel-order.ts    # Use case
│   │   ├── orders.test.ts
│   │   └── index.ts
│   └── products/
│       └── ...
├── shared/
│   ├── database/
│   │   ├── connection.ts
│   │   └── migrations/
│   ├── http/
│   │   ├── server.ts
│   │   └── middleware/
│   └── utils/
│       ├── date.ts
│       └── validation.ts
├── config/
│   └── index.ts
└── main.ts
```

### Feature Internal Structure

Each feature folder follows a consistent pattern:

```
feature/
├── [entity].ts           # Core entity/model
├── [entity]-service.ts   # Business logic
├── [entity]-repository.ts # Data access
├── [entity]-controller.ts # HTTP handlers (if applicable)
├── [entity]-validator.ts  # Input validation (if complex)
├── [use-case].ts         # Individual use cases (optional)
├── [feature].test.ts     # Tests
└── index.ts              # Public API (re-exports)
```

### Pros & Cons

| Pros | Cons |
|------|------|
| Features are self-contained | Some shared code needed |
| Easy to find related code | May have duplication |
| Changes localized to folder | Requires discipline |
| Features can be extracted | Cross-feature logic tricky |
| Scales to medium-large apps | - |

### When to Use

- Most web applications
- Teams organized by feature
- 10-100 files
- Applications that will grow

---

## Pattern 3: Hexagonal/Ports-Adapters

Best for complex domains requiring high testability.

### Structure

```
src/
├── domain/                    # Core business logic (NO external deps)
│   ├── order/
│   │   ├── order.ts           # Entity with behavior
│   │   ├── order-service.ts   # Domain service
│   │   ├── order.repository.ts # Port (interface only)
│   │   └── order.errors.ts    # Domain errors
│   ├── user/
│   │   ├── user.ts
│   │   ├── user-service.ts
│   │   └── user.repository.ts
│   └── shared/
│       ├── entity.ts          # Base entity
│       └── value-object.ts    # Base value object
│
├── application/               # Use cases, orchestration
│   ├── order/
│   │   ├── create-order.ts    # Use case
│   │   ├── cancel-order.ts
│   │   └── get-order.ts
│   └── user/
│       ├── register-user.ts
│       └── authenticate-user.ts
│
├── infrastructure/            # External world adapters
│   ├── persistence/
│   │   ├── postgres/
│   │   │   ├── postgres-order-repository.ts
│   │   │   └── postgres-user-repository.ts
│   │   └── connection.ts
│   ├── http/
│   │   ├── express-server.ts
│   │   ├── routes/
│   │   │   ├── order-routes.ts
│   │   │   └── user-routes.ts
│   │   └── middleware/
│   ├── messaging/
│   │   └── rabbitmq-publisher.ts
│   └── external/
│       ├── stripe-payment.ts
│       └── sendgrid-email.ts
│
├── config/
│   └── index.ts
│
└── main.ts                    # Composition root (wires everything)
```

### Dependency Direction

```
┌─────────────────────────────────────────────────┐
│                  Infrastructure                  │
│  (HTTP, Database, External APIs, Messaging)     │
└───────────────────────┬─────────────────────────┘
                        │ depends on
                        ▼
┌─────────────────────────────────────────────────┐
│                   Application                    │
│        (Use Cases, Orchestration)               │
└───────────────────────┬─────────────────────────┘
                        │ depends on
                        ▼
┌─────────────────────────────────────────────────┐
│                     Domain                       │
│  (Entities, Value Objects, Domain Services)     │
│         NO EXTERNAL DEPENDENCIES                │
└─────────────────────────────────────────────────┘
```

### Pros & Cons

| Pros | Cons |
|------|------|
| Domain isolated from tech | More files and folders |
| Highly testable | Higher learning curve |
| Tech can be swapped | Overhead for simple apps |
| Clear dependency direction | More interfaces/abstractions |
| Scales to large systems | - |

### When to Use

- Complex business domains
- High testability requirements
- Long-lived systems (5+ years)
- Domain-Driven Design projects
- Multiple UI/API consumers

---

## Pattern 4: Module-Based (Monorepo)

Best for large systems with multiple applications or teams.

### Structure

```
packages/
├── core/                      # Shared types and utilities
│   ├── src/
│   │   ├── types/
│   │   │   ├── user.ts
│   │   │   └── order.ts
│   │   ├── utils/
│   │   │   ├── date.ts
│   │   │   └── validation.ts
│   │   └── index.ts
│   ├── package.json
│   └── tsconfig.json
│
├── orders/                    # Order domain package
│   ├── src/
│   │   ├── domain/
│   │   │   ├── order.ts
│   │   │   └── order-service.ts
│   │   ├── infrastructure/
│   │   │   └── order-repository.ts
│   │   ├── application/
│   │   │   ├── create-order.ts
│   │   │   └── cancel-order.ts
│   │   └── index.ts
│   ├── package.json           # depends on @company/core
│   └── tsconfig.json
│
├── users/                     # User domain package
│   ├── src/
│   │   └── ...
│   └── package.json
│
├── api/                       # HTTP API application
│   ├── src/
│   │   ├── routes/
│   │   ├── middleware/
│   │   └── main.ts
│   └── package.json           # depends on @company/orders, @company/users
│
├── web/                       # Frontend application
│   ├── src/
│   │   └── ...
│   └── package.json
│
├── worker/                    # Background job processor
│   ├── src/
│   │   └── ...
│   └── package.json
│
└── package.json               # Workspace root
```

### Package Relationships

```
                    ┌──────────────┐
                    │     core     │
                    │   (shared)   │
                    └──────┬───────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │  orders  │    │  users   │    │ products │
    │ (domain) │    │ (domain) │    │ (domain) │
    └────┬─────┘    └────┬─────┘    └────┬─────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
    ┌──────────┐  ┌──────────┐  ┌──────────┐
    │   api    │  │   web    │  │  worker  │
    │  (app)   │  │  (app)   │  │  (app)   │
    └──────────┘  └──────────┘  └──────────┘
```

### Pros & Cons

| Pros | Cons |
|------|------|
| Independent deployments | Complex tooling (nx, turborepo) |
| Clear team ownership | Dependency management overhead |
| Enforced boundaries | Longer initial setup |
| Code sharing controlled | Cross-package refactoring hard |
| Parallel development | - |

### When to Use

- Large systems (100+ files)
- Multiple applications (API, web, mobile)
- Multiple teams
- Microservices architecture
- Shared libraries needed

---

## Shared Code Guidelines

### What Goes in shared/

```
shared/
├── database/              # Database connection, base repository
├── http/                  # Server setup, common middleware
├── messaging/             # Queue connections, base publishers
├── utils/                 # Pure utility functions
│   ├── date.ts
│   ├── string.ts
│   └── validation.ts
├── types/                 # Shared type definitions
│   └── common.ts
└── errors/                # Base error classes
    └── http-error.ts
```

### Shared Code Rules

1. **Rule of Three:** Only extract to shared after 3+ usages
2. **Stability:** Shared code should rarely change
3. **Independence:** No feature-specific logic
4. **Pure Functions:** Prefer stateless utilities
5. **Clear API:** Well-documented public interface

### What Stays in Features

- Feature-specific utilities
- Feature-specific types
- Code used by only 1-2 features
- Frequently changing code

---

## Folder Depth Guidelines

### Maximum Recommended Depth

```
src/                       # Level 1
├── features/              # Level 2
│   └── orders/            # Level 3
│       └── use-cases/     # Level 4 (MAX for most cases)
│           └── create-order.ts
```

### Flattening Deep Structures

**Before (too deep):**
```
src/features/orders/domain/entities/order/line-item/discount.ts
```

**After (flattened):**
```
src/features/orders/order-line-item.ts
src/features/orders/line-item-discount.ts
```

### When Depth is Acceptable

- Clear hierarchy (domain > subdomain > entity)
- Each level has multiple siblings
- Folder names are meaningful
- Navigation is intuitive

---

## Migration Between Patterns

### Layer-Based → Feature-Based

1. Create feature folders
2. Move related files together
3. Update imports
4. Create feature index.ts
5. Remove empty layer folders

### Feature-Based → Hexagonal

1. Create domain/application/infrastructure
2. Move entities to domain
3. Extract interfaces (ports)
4. Move implementations to infrastructure
5. Move orchestration to application

### Monolith → Monorepo

1. Identify domain boundaries
2. Create package per domain
3. Extract shared code to core
4. Set up workspace tooling
5. Migrate applications incrementally
