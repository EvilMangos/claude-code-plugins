---
name: software-design-principles
description: >
  Use this skill when performing code reviews, refactoring, making architectural decisions,
  or evaluating code quality. Also use when the user asks about SOLID principles, design patterns,
  coupling/cohesion, clean architecture, domain-driven design, or software design fundamentals.
---

# Software Design Principles

This skill provides foundational knowledge for evaluating and improving software design quality.
Use these principles when refactoring code, reviewing changes, or making architectural decisions.

## SOLID Principles - Quick Reference

### Single Responsibility Principle (SRP)

A class/module should have only one reason to change.

**Violation signals:**
- Class name contains "And" or "Manager" doing unrelated things
- Changes to one feature require modifying unrelated code
- Hard to describe what a class does in one sentence

**Fix:** Extract separate classes for each responsibility.

### Open/Closed Principle (OCP)

Open for extension, closed for modification.

**Violation signals:**
- Adding features requires modifying existing switch/if chains
- New types require changes in multiple places
- Core logic changes for each new variation

**Fix:** Use polymorphism, strategy pattern, or plugin architecture.

### Liskov Substitution Principle (LSP)

Subtypes must be substitutable for their base types.

**Violation signals:**
- Subclass throws exceptions for inherited methods
- Subclass overrides method to do nothing
- Type checks before calling methods (`instanceof`)

**Fix:** Redesign hierarchy or use composition over inheritance.

### Interface Segregation Principle (ISP)

Clients should not depend on interfaces they don't use.

**Violation signals:**
- Implementing classes have empty/throwing methods
- Interface has 10+ methods
- Changes to interface affect unrelated implementers

**Fix:** Split into smaller, focused interfaces.

### Dependency Inversion Principle (DIP)

Depend on abstractions, not concretions.

**Violation signals:**
- High-level modules import low-level modules directly
- Classes instantiate their dependencies with `new`
- Hard to test without real database/network

**Fix:** Inject dependencies through constructor/parameters.

## Coupling and Cohesion

### Coupling (aim for LOW)

Degree of interdependence between modules.

| Type | Description | Quality |
|------|-------------|---------|
| **Content** | Module modifies another's internals | Worst |
| **Common** | Modules share global data | Bad |
| **Control** | Passing flags to control behavior | Poor |
| **Stamp** | Passing entire objects when few fields needed | Fair |
| **Data** | Passing only needed data | Good |
| **Message** | Communication via well-defined interfaces | Best |

**Reduce coupling by:**
- Using dependency injection
- Defining clear interfaces/contracts
- Avoiding global state
- Passing only required data

### Cohesion (aim for HIGH)

Degree to which elements within a module belong together.

| Type | Description | Quality |
|------|-------------|---------|
| **Coincidental** | Random grouping | Worst |
| **Logical** | Related by category, not function | Poor |
| **Temporal** | Run at same time | Poor |
| **Procedural** | Part of same procedure | Fair |
| **Communicational** | Operate on same data | Good |
| **Sequential** | Output of one is input to next | Good |
| **Functional** | All contribute to single task | Best |

**Increase cohesion by:**
- Grouping related functionality
- Splitting classes that do multiple things
- Moving methods closer to the data they use

## Design Patterns - When to Apply

### Creational Patterns

| Pattern | Use When |
|---------|----------|
| **Factory** | Object creation logic is complex or varies |
| **Builder** | Many optional parameters, step-by-step construction |
| **Singleton** | Exactly one instance needed (use sparingly) |

### Structural Patterns

| Pattern | Use When |
|---------|----------|
| **Adapter** | Making incompatible interfaces work together |
| **Decorator** | Adding behavior without modifying class |
| **Facade** | Simplifying complex subsystem interface |

### Behavioral Patterns

| Pattern | Use When |
|---------|----------|
| **Strategy** | Swappable algorithms at runtime |
| **Observer** | Objects need notification of state changes |
| **Command** | Encapsulating requests as objects (undo, queue) |

## Domain-Driven Design - Quick Reference

### Strategic Patterns

| Pattern | Purpose |
|---------|---------|
| **Bounded Context** | Boundary where a domain model applies |
| **Ubiquitous Language** | Shared vocabulary between devs and domain experts |
| **Context Mapping** | Relationships between bounded contexts |
| **Anti-Corruption Layer** | Translates between external and internal models |

### Tactical Patterns

| Pattern | Description |
|---------|-------------|
| **Entity** | Object with identity (equality by ID) |
| **Value Object** | Immutable object (equality by attributes) |
| **Aggregate** | Cluster with root entity, transactional boundary |
| **Repository** | Collection-like interface for aggregates |
| **Domain Service** | Logic that doesn't fit in entities |
| **Domain Event** | Record of something that happened |
| **Specification** | Reusable business rule |

### When to Use DDD

**Good fit:**
- Complex business logic
- Domain experts available
- Long-lived projects
- Multiple bounded contexts

**Poor fit:**
- Simple CRUD applications
- Technical/infrastructure-focused systems
- Short-term projects
- No domain expert access

## Code Smells Indicating Design Issues

### Bloaters
- **Long Method** - Extract smaller methods
- **Large Class** - Split by responsibility
- **Long Parameter List** - Introduce parameter object

### Object-Orientation Abusers
- **Switch Statements** - Replace with polymorphism
- **Refused Bequest** - Reconsider inheritance hierarchy
- **Parallel Inheritance** - Consider composition

### Change Preventers
- **Divergent Change** - One class changed for many reasons (split it)
- **Shotgun Surgery** - One change affects many classes (consolidate)

### Couplers
- **Feature Envy** - Method uses another class's data more than its own
- **Inappropriate Intimacy** - Classes know too much about each other
- **Message Chains** - `a.getB().getC().getD()` - introduce facade

## Applying Principles in Practice

### During Refactoring

1. Identify which principle is violated
2. Choose smallest change that addresses it
3. Apply incrementally with tests passing
4. Stop when code is "good enough" - avoid gold plating

### During Code Review

Evaluate against principles but consider context:
- Is the violation causing actual problems?
- Does fixing it add disproportionate complexity?
- Is the codebase consistent in this area?

Flag as **blocking** only for clear architectural violations. Suggest improvements for minor issues.

### When Designing New Features

1. Start simple - don't pre-optimize for flexibility
2. Apply patterns when complexity demands it
3. Prefer composition over inheritance
4. Design for testability (naturally leads to good design)

## Anti-Patterns to Recognize

| Anti-Pattern | Problem | Better Approach |
|--------------|---------|-----------------|
| **God Object** | One class does everything | Split by responsibility |
| **Anemic Domain** | Data classes + separate logic | Rich domain objects |
| **Golden Hammer** | Using one pattern everywhere | Choose per context |
| **Premature Abstraction** | Abstracting before needed | Wait for duplication |
| **Speculative Generality** | Building for hypothetical futures | YAGNI - build what's needed |

## Additional Resources

For detailed explanations and extensive examples, consult:

- **`references/solid-principles.md`** - Full SOLID with language-specific examples
- **`references/design-patterns.md`** - GoF patterns (Creational, Structural, Behavioral)
- **`references/domain-driven-design.md`** - DDD strategic & tactical patterns
- **`references/coupling-cohesion.md`** - Metrics, evaluation techniques, and refactoring strategies
- **`references/dependency-injection.md`** - DI containers, patterns, and testing strategies

### Related Skills

When applying these principles in code review, consult the **code-review-checklist** skill for:
- Systematic review workflow
- Blocking vs non-blocking issue categorization
- Security and performance checklists
- Review output format templates
