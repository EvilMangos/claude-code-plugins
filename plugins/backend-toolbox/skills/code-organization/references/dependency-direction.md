# Dependency Direction Rules

This reference defines the rules for dependency direction between modules and packages. Correct dependency direction is critical for maintainability, testability, and avoiding coupling to implementation details.

---

## The Core Rule

> **Modules must never depend on implementation details of other modules. Dependencies must flow toward abstractions, not away from them.**

This means:

1. **Business logic modules must NOT import from infrastructure modules** (database, HTTP, messaging, etc.)
2. **Contracts (interfaces/ports) must live in a neutral location** - never owned by the provider
3. **Infrastructure modules depend on business logic** through ports and adapters, not the reverse

---

## Allowed Dependency Patterns

### Pattern 1: Shared Contracts Layer

Both consumer and provider depend on a shared contracts layer:

```
contracts/              # Owns the interfaces - neutral territory
├── order-repository.ts # interface OrderRepository
└── email-sender.ts     # interface EmailSender

domain/                 # Business logic
└── order-service.ts    # imports from contracts/, NOT from infrastructure/

infrastructure/         # Implementations
├── postgres-order-repository.ts  # imports from contracts/, implements interface
└── sendgrid-email-sender.ts      # imports from contracts/, implements interface
```

**Import direction:**
```
domain/order-service.ts      → imports → contracts/order-repository.ts
infrastructure/postgres-*.ts → imports → contracts/order-repository.ts
```

**Never:**
```
domain/order-service.ts → imports → infrastructure/postgres-order-repository.ts  # WRONG!
```

### Pattern 2: Hexagonal (Ports & Adapters)

Domain owns its ports (interfaces), adapters depend inward on domain:

```
domain/                 # Core - owns ports
├── order.ts            # Entity
├── order-service.ts    # Domain service
└── ports/
    ├── order-repository.ts    # Port (interface) - domain defines what it needs
    └── payment-gateway.ts     # Port (interface)

adapters/               # Implementations depend on domain
├── driven/             # Secondary adapters (called by domain)
│   ├── postgres-order-repository.ts  # implements domain/ports/order-repository
│   └── stripe-payment-gateway.ts     # implements domain/ports/payment-gateway
└── driving/            # Primary adapters (call into domain)
    └── rest-api-controller.ts        # calls domain/order-service
```

**Import direction:**
```
adapters/postgres-order-repository.ts → imports → domain/ports/order-repository.ts
adapters/rest-api-controller.ts       → imports → domain/order-service.ts
```

**The key principle:** Domain is the center. Everything points inward toward domain.

---

## Forbidden Dependency Patterns

### Pattern: Business Logic Imports Infrastructure

```typescript
// WRONG - domain imports infrastructure
// domain/order-service.ts
import { PostgresOrderRepository } from '../infrastructure/postgres-order-repository';  // VIOLATION!
import { SendGridEmailSender } from '../infrastructure/sendgrid-email-sender';          // VIOLATION!

class OrderService {
  private repo = new PostgresOrderRepository();  // Coupled to implementation
}
```

**Why it's wrong:**
- Business logic is coupled to specific database technology
- Cannot test without real database
- Changing database requires changing business logic
- Violates Dependency Inversion Principle

### Pattern: Provider Owns Its Contract

```typescript
// WRONG - infrastructure module exports its own interface
// infrastructure/postgres-order-repository.ts
export interface OrderRepository {  // Interface defined by the provider
  save(order: Order): Promise<void>;
}

export class PostgresOrderRepository implements OrderRepository {
  // ...
}

// domain/order-service.ts
import { OrderRepository } from '../infrastructure/postgres-order-repository';  // VIOLATION!
// Domain now depends on infrastructure module, even though it only uses the interface
```

**Why it's wrong:**
- Consumer (domain) has import dependency on provider module (infrastructure)
- Provider can change/remove interface without domain's consent
- Interface is implementation-biased, not consumer-biased
- Package dependency graph shows domain → infrastructure (wrong direction)

### Pattern: Circular Dependencies Through Contracts

```typescript
// WRONG - contracts import from domain or infrastructure
// contracts/order-repository.ts
import { Order } from '../domain/order';  // Creates cycle if domain imports contracts
import { DatabaseConnection } from '../infrastructure/database';  // VIOLATION!
```

**Why it's wrong:**
- Contracts layer should be dependency-free (leaf in dependency graph)
- Circular dependencies break module boundaries
- Makes contracts non-portable

---

## The Contract Location Rule

> **Contracts (interfaces/ports) must be defined in a location that neither the consumer nor the provider owns.**

### Correct Locations for Contracts

| Project Type | Contract Location | Notes |
|--------------|-------------------|-------|
| **Single package** | `src/contracts/` or `src/ports/` | Dedicated folder, no implementation code |
| **Monorepo** | `packages/contracts/` | Shared package that other packages depend on |
| **Hexagonal** | `src/domain/ports/` | Domain owns ports (intentional - domain defines needs) |
| **DDD** | `src/domain/` (domain services as interfaces) | Domain defines contracts for infrastructure |

### Incorrect Locations for Contracts

| Location | Why Wrong |
|----------|-----------|
| With the provider (`infrastructure/postgres-order-repository.ts`) | Consumer depends on provider's module |
| With the consumer only | Provider has no access to implement |
| Inline in implementation file | Cannot be imported separately |

---

## Dependency Direction by Layer

### Standard Layered Architecture

```
┌─────────────────────────────────────┐
│           Presentation              │  → depends on Application
├─────────────────────────────────────┤
│           Application               │  → depends on Domain + Contracts
├─────────────────────────────────────┤
│             Domain                  │  → depends on Contracts (or owns ports)
├─────────────────────────────────────┤
│            Contracts                │  → depends on NOTHING (leaf node)
├─────────────────────────────────────┤
│          Infrastructure             │  → depends on Contracts + Domain
└─────────────────────────────────────┘

Allowed: Down and toward Contracts
Forbidden: Up (Infrastructure → Domain logic, not ports)
```

### Dependency Rules by Layer

| From Layer | Can Depend On | Cannot Depend On |
|------------|---------------|------------------|
| **Presentation** | Application, Domain types, Contracts | Infrastructure |
| **Application** | Domain, Contracts | Infrastructure, Presentation |
| **Domain** | Contracts (or owns ports) | Infrastructure, Application, Presentation |
| **Contracts** | Nothing (primitives only) | All other layers |
| **Infrastructure** | Contracts, Domain types | Application, Presentation |

---

## Applying the Rules

### Code Review Checklist

When reviewing code, check for these violations:

- [ ] Does any file in `domain/` or `application/` import from `infrastructure/`?
- [ ] Are interfaces defined in the same file as their implementation?
- [ ] Does the contracts layer import from domain or infrastructure?
- [ ] Are there direct instantiations of infrastructure classes in business logic (`new PostgresRepo()`)?
- [ ] Do infrastructure modules export interfaces that domain consumes?

### Refactoring Violations

**Step 1: Identify the contract**
```typescript
// Current violation in infrastructure/
export interface OrderRepository { ... }  // Move this
export class PostgresOrderRepository implements OrderRepository { ... }
```

**Step 2: Move contract to neutral location**
```typescript
// contracts/order-repository.ts (new file)
export interface OrderRepository {
  save(order: Order): Promise<void>;
  findById(id: string): Promise<Order | null>;
}
```

**Step 3: Update imports**
```typescript
// domain/order-service.ts
import { OrderRepository } from '../contracts/order-repository';  // Correct

// infrastructure/postgres-order-repository.ts
import { OrderRepository } from '../contracts/order-repository';  // Correct
export class PostgresOrderRepository implements OrderRepository { ... }
```

**Step 4: Inject at composition root**
```typescript
// main.ts (composition root)
import { OrderService } from './domain/order-service';
import { PostgresOrderRepository } from './infrastructure/postgres-order-repository';

const repo = new PostgresOrderRepository(connectionPool);
const service = new OrderService(repo);  // Dependency injected
```

---

## Common Questions

### Q: Can domain types be used in contracts?

**Yes**, but only domain **types/entities**, not domain **services** or **logic**:

```typescript
// contracts/order-repository.ts
import { Order } from '../domain/order';  // OK - Order is a type/entity

export interface OrderRepository {
  save(order: Order): Promise<void>;
}
```

This is acceptable because:
- `Order` is a data structure, not behavior
- Contracts describe operations on domain types
- No circular dependency (domain types don't import contracts)

### Q: What if I need infrastructure types in my interface?

**Extract the minimal type into contracts**:

```typescript
// WRONG - using infrastructure type
import { Pool } from 'pg';  // Infrastructure dependency!

export interface DatabaseConnection {
  getPool(): Pool;  // Leaks pg library
}

// CORRECT - abstract away infrastructure types
export interface DatabaseConnection {
  query<T>(sql: string, params: unknown[]): Promise<T[]>;
  transaction<T>(fn: (conn: DatabaseConnection) => Promise<T>): Promise<T>;
}
```

### Q: Should I create interfaces for everything?

**No.** Only create interfaces (ports) for:

1. External dependencies (database, HTTP, file system, third-party services)
2. Boundaries between major modules/packages
3. Components that need to be mocked in tests
4. Components with multiple implementations

**Don't** create interfaces for:
- Internal domain logic that won't change
- Value objects and entities
- Purely computational functions with no side effects

---

## Related References

- `design-patterns/references/dependency-injection.md` - DI patterns and container usage
- `design-patterns/references/solid-principles.md` - Dependency Inversion Principle details
- `design-assessment/references/coupling-cohesion.md` - Coupling types and measurement
- `code-organization/SKILL.md` - Folder structure patterns including hexagonal
