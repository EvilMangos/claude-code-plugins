---
name: design-patterns
description: This skill should be used when the user asks about design patterns, SOLID principles, dependency injection, or code architecture. Common triggers include "which pattern should I use", "how should I structure this", "apply SOLID principles", "set up dependency injection", "factory pattern", "repository pattern", "strategy pattern", "DDD", "domain model", "singleton", "observer pattern", "decorator vs inheritance", "refactor to use strategy", "how to make this more testable", "decouple my classes", "reduce coupling between components", "what pattern for...", "implement the repository pattern", "use abstract factory", "apply command pattern", "event-driven design", or when the user mentions design patterns by name.
version: 0.1.0
---

# Design Patterns

Patterns and principles for structuring code correctly. Use when implementing features or refactoring.

## SOLID Principles - How to Apply

### Single Responsibility Principle (SRP)

> A class should have only one reason to change.

**Applying SRP:**

1. Identify reasons for change - List what business requirements could cause the class to change
2. Group related functionality - Methods that change together belong together
3. Extract classes - Create new classes for each distinct responsibility
4. Use composition - Coordinate multiple classes from a higher level

```typescript
// Before: Multiple responsibilities
class User {
  validate(): boolean { /* validation */ }
  save(): void { /* database */ }
  sendWelcomeEmail(): void { /* email */ }
}

// After: Separated responsibilities
class User { /* just data and domain logic */ }
class UserValidator { validate(user: User): boolean { /* ... */ } }
class UserRepository { save(user: User): void { /* ... */ } }
class WelcomeEmailSender { send(user: User): void { /* ... */ } }
```

### Open/Closed Principle (OCP)

> Open for extension, closed for modification.

**Applying OCP:**

1. Use polymorphism - Define interfaces, let implementations vary
2. Strategy Pattern - Encapsulate algorithms, swap at runtime
3. Decorator Pattern - Add behavior by wrapping
4. Plugin Architecture - Load extensions dynamically

```typescript
// Before: Must modify for each new shape
function calculateArea(shape: Shape): number {
  if (shape.type === 'circle') return Math.PI * shape.radius ** 2;
  if (shape.type === 'rectangle') return shape.width * shape.height;
  // Must add new if-branch for each shape
}

// After: Extend without modification
interface Shape {
  calculateArea(): number;
}

class Circle implements Shape {
  calculateArea(): number { return Math.PI * this.radius ** 2; }
}
// Adding new shapes doesn't modify existing code
```

### Liskov Substitution Principle (LSP)

> Subtypes must be substitutable for their base types.

**Applying LSP:**

- Subtypes must honor base class contracts
- Cannot strengthen preconditions (require more)
- Cannot weaken postconditions (guarantee less)
- Must maintain all invariants

**Fixing violations:**

- Reconsider the hierarchy - maybe inheritance is wrong
- Use composition instead of inheritance
- Extract common interface without forcing inheritance

### Interface Segregation Principle (ISP)

> Clients should not depend on interfaces they don't use.

**Applying ISP:**

1. Identify clients - Who uses this interface?
2. Group by usage - Which methods does each client need?
3. Extract interfaces - Create focused interfaces per client need
4. Compose - Classes can implement multiple small interfaces

```typescript
// Before: Fat interface
interface Worker {
  work(): void;
  eat(): void;
  sleep(): void;
}

// After: Segregated interfaces
interface Workable { work(): void; }
interface Feedable { eat(): void; }
interface Restable { sleep(): void; }

class Human implements Workable, Feedable, Restable { /* all */ }
class Robot implements Workable { /* only work */ }
```

### Dependency Inversion Principle (DIP)

> Depend on abstractions, not concretions.

**Applying DIP:**

1. Define interfaces for dependencies
2. **Locate interfaces in a contracts layer** (not in consumer or provider)
3. Inject dependencies through constructor
4. Keep high-level modules independent of low-level details

**Critical - Interface Location:**

- Interfaces must NOT live in the consumer's module or the provider's module
- Create a separate `contracts/` layer (or package in monorepos)
- Exception: In hexagonal architecture, ports live in the domain layer

```typescript
// Before: Direct dependency
class OrderService {
  private db = new MySQLDatabase();
  private emailer = new SendGridEmailer();
}

// After: Depend on abstractions from contracts layer
// contracts/order-repository.ts - Interface lives here
interface OrderRepository { save(order: Order): void; }

// domain/order-service.ts - Depends on contracts
import { OrderRepository } from '../contracts/order-repository';
class OrderService {
  constructor(private repository: OrderRepository) {}
}

// infrastructure/mysql-repository.ts - Implements contracts
import { OrderRepository } from '../contracts/order-repository';
class MySQLOrderRepository implements OrderRepository { /* ... */ }
```

## Design Patterns Quick Reference

### Creational Patterns

| Pattern              | Use When                             | Example                                      |
|----------------------|--------------------------------------|----------------------------------------------|
| **Factory Method**   | Object creation varies by context    | `createPaymentProcessor(type)`               |
| **Abstract Factory** | Families of related objects          | UI component factories (Material, Bootstrap) |
| **Builder**          | Complex object, many optional params | `QueryBuilder().select().from().where()`     |
| **Singleton**        | Exactly one instance needed          | Configuration (prefer DI instead)            |

### Structural Patterns

| Pattern       | Use When                             | Example                                         |
|---------------|--------------------------------------|-------------------------------------------------|
| **Adapter**   | Make incompatible interfaces work    | Wrapping legacy/third-party APIs                |
| **Decorator** | Add behavior without modifying class | Logging, caching, validation wrappers           |
| **Facade**    | Simplify complex subsystem           | `VideoPlayer.play()` hiding decode/render/audio |
| **Composite** | Tree/hierarchy structures            | File system (files and folders)                 |

### Behavioral Patterns

| Pattern      | Use When                            | Example                             |
|--------------|-------------------------------------|-------------------------------------|
| **Strategy** | Swappable algorithms at runtime     | Sorting strategies, payment methods |
| **Observer** | Notify multiple objects of changes  | Event emitters, pub/sub             |
| **Command**  | Encapsulate operations (undo/queue) | Text editor commands, job queues    |
| **State**    | Behavior varies by internal state   | Order status transitions            |

## Domain-Driven Design Patterns

### When to Use DDD

**Good fit:** Complex business logic, domain experts available, long-lived projects
**Poor fit:** Simple CRUD, short-term projects, no domain expert access

### Tactical Patterns

| Pattern            | What It Is                                       | When to Use                                  |
|--------------------|--------------------------------------------------|----------------------------------------------|
| **Entity**         | Object with identity (equality by ID)            | Things that have lifecycle, change over time |
| **Value Object**   | Immutable, equality by attributes                | Money, Address, DateRange, typed IDs         |
| **Aggregate**      | Cluster with root entity, transactional boundary | Order with LineItems                         |
| **Repository**     | Collection-like interface for aggregates         | `OrderRepository.findById()`                 |
| **Domain Service** | Logic that doesn't fit in entities               | Cross-aggregate operations                   |
| **Domain Event**   | Record of something that happened                | `OrderSubmitted`, `PaymentReceived`          |
| **Factory**        | Complex object creation                          | `OrderFactory.createFromCart()`              |

### Strategic Patterns

| Pattern                   | Purpose                                         |
|---------------------------|-------------------------------------------------|
| **Bounded Context**       | Boundary where a domain model applies           |
| **Ubiquitous Language**   | Shared vocabulary in code and conversation      |
| **Anti-Corruption Layer** | Translates between external and internal models |
| **Context Mapping**       | Relationships between bounded contexts          |

## Dependency Injection Patterns

### Injection Types

| Type                      | When to Use                            |
|---------------------------|----------------------------------------|
| **Constructor Injection** | Required dependencies (default choice) |
| **Setter Injection**      | Optional dependencies                  |
| **Method Injection**      | Per-call varying dependencies          |

### Best Practices

1. **Depend on abstractions** - Interfaces, not concrete classes
2. **Locate interfaces in contracts layer** - Not in consumer or provider modules
3. **Inject what you need** - Not the container itself
4. **Keep constructors simple** - Assignment only, no logic
5. **Avoid circular dependencies** - Break with interfaces or events

```typescript
// Good: Clear dependencies
class OrderService {
  constructor(
    private repository: OrderRepository,
    private emailer: EmailSender
  ) {}
}

// Bad: Hidden dependencies
class OrderService {
  createOrder(): void {
    const repo = ServiceLocator.get('repo');  // Hidden!
  }
}
```

### Lifetimes

| Lifetime      | When to Use                                  |
|---------------|----------------------------------------------|
| **Singleton** | Stateless services, connection pools, config |
| **Transient** | Stateful services, per-use instances         |
| **Scoped**    | Per-request services, unit of work           |

## Pattern Selection Guide

| Problem                            | Consider Pattern      |
|------------------------------------|-----------------------|
| Object creation is complex         | Factory, Builder      |
| Need single instance               | Singleton (prefer DI) |
| Incompatible interfaces            | Adapter               |
| Add responsibilities dynamically   | Decorator             |
| Simplify complex subsystem         | Facade                |
| Tree/hierarchy structures          | Composite             |
| Swappable algorithms               | Strategy              |
| Notify multiple objects of changes | Observer              |
| Undo/redo, queuing operations      | Command               |
| Behavior varies by state           | State                 |
| Complex domain logic               | DDD Tactical Patterns |
| Large system with multiple teams   | Bounded Contexts      |

## Additional Resources

For detailed explanations and code examples:

- **`references/solid-principles.md`** - Full SOLID with multi-language examples
- **`references/design-patterns.md`** - Complete GoF patterns catalog
- **`references/domain-driven-design.md`** - DDD strategic & tactical patterns
- **`references/dependency-injection.md`** - DI containers, testing strategies

### Related Skills

When assessing code quality, consult the **design-assessment** skill for:

- Code smell identification
- Coupling/cohesion metrics
- SOLID violation signals
- Anti-pattern recognition
