---
name: design-assessment
description: This skill should be used when the user asks to "assess design quality", "identify code smells", "check coupling and cohesion", "evaluate architecture", "is this well designed", "design review", "find design issues", "architecture assessment", "quality assessment", or needs to identify structural problems in existing code.
version: 0.1.0
---

# Design Assessment

Identify and evaluate design issues in existing code. Use this skill during code review or when assessing code quality.

## Code Smells Quick Reference

### Bloaters (code that has grown too large)

| Smell                   | Signs                                           | Impact                                       |
|-------------------------|-------------------------------------------------|----------------------------------------------|
| **Long Method**         | Method > 20-30 lines, multiple responsibilities | Hard to understand, test, reuse              |
| **Large Class**         | Class > 200-300 lines, many unrelated methods   | Low cohesion, hard to modify                 |
| **Long Parameter List** | > 3-4 parameters                                | Hard to call, often indicates missing object |
| **Primitive Obsession** | Using primitives instead of small objects       | Scattered validation, no encapsulation       |
| **Data Clumps**         | Same group of variables appear together         | Missing abstraction                          |

### Object-Orientation Abusers

| Smell                    | Signs                                       | Impact                          |
|--------------------------|---------------------------------------------|---------------------------------|
| **Switch Statements**    | Type-based switches/if-chains               | Violates OCP, changes ripple    |
| **Refused Bequest**      | Subclass doesn't use inherited methods      | Wrong hierarchy                 |
| **Parallel Inheritance** | Creating subclass requires another subclass | Tight coupling                  |
| **Alternative Classes**  | Different classes with similar interfaces   | Duplication, missed abstraction |

### Change Preventers

| Smell                    | Signs                                        | Impact              |
|--------------------------|----------------------------------------------|---------------------|
| **Divergent Change**     | One class changed for many different reasons | Violates SRP        |
| **Shotgun Surgery**      | One change requires edits in many classes    | High coupling       |
| **Parallel Inheritance** | Adding subclass requires adding another      | Coupled hierarchies |

### Couplers (excessive coupling between classes)

| Smell                      | Signs                                              | Impact                            |
|----------------------------|----------------------------------------------------|-----------------------------------|
| **Feature Envy**           | Method uses another class's data more than its own | Misplaced responsibility          |
| **Inappropriate Intimacy** | Classes access each other's private parts          | Tight coupling                    |
| **Message Chains**         | `a.getB().getC().getD()`                           | Fragile, Law of Demeter violation |
| **Middle Man**             | Class delegates most work to another               | Unnecessary indirection           |

### Dispensables (unnecessary code)

| Smell                      | Signs                                | Impact                     |
|----------------------------|--------------------------------------|----------------------------|
| **Dead Code**              | Unreachable or unused code           | Noise, maintenance burden  |
| **Speculative Generality** | Unused abstractions "for the future" | Complexity without benefit |
| **Lazy Class**             | Class that doesn't do enough         | Unnecessary indirection    |
| **Duplicate Code**         | Same logic in multiple places        | Maintenance burden, bugs   |

## SOLID Violation Signals

### Single Responsibility Principle (SRP)

**Violation signals:**

- Class name contains "And" or "Manager" doing unrelated things
- Changes to one feature require modifying unrelated code
- Hard to describe what a class does in one sentence
- Class has dependencies for unrelated concerns

**Review question:** "What are all the reasons this class might change?"

### Open/Closed Principle (OCP)

**Violation signals:**

- Adding a new type requires modifying existing switch/if chains
- New types require changes in multiple places
- Core logic changes for each new variation

**Review question:** "Can I add a new variant without modifying existing code?"

### Liskov Substitution Principle (LSP)

**Violation signals:**

- Subclass throws exceptions for inherited methods
- Subclass overrides method to do nothing
- Type checks before calling methods (`instanceof`)
- Subclass violates base class invariants

**Review question:** "Can I substitute any subtype without breaking behavior?"

### Interface Segregation Principle (ISP)

**Violation signals:**

- Implementing classes have empty/throwing methods
- Interface has 10+ methods
- Changes to interface affect unrelated implementers

**Review question:** "Do all clients use all methods of this interface?"

### Dependency Inversion Principle (DIP)

**Violation signals:**

- High-level modules import low-level modules directly
- Classes instantiate dependencies with `new`
- Hard to test without real database/network

**Review question:** "Does this depend on abstractions or concrete implementations?"

## Coupling Assessment

### Coupling Types (worst to best)

| Type        | Description                                   | Red Flag                               |
|-------------|-----------------------------------------------|----------------------------------------|
| **Content** | Module modifies another's internals           | Direct field access across modules     |
| **Common**  | Modules share global data                     | Global variables, shared mutable state |
| **Control** | Passing flags to control behavior             | Boolean parameters, type switches      |
| **Stamp**   | Passing entire objects when few fields needed | Large DTOs passed around               |
| **Data**    | Passing only needed data                      | Clean interfaces                       |
| **Message** | Communication via well-defined interfaces     | Events, clear contracts                |

### Coupling Red Flags in Code Review

- [ ] Does this change introduce new dependencies between modules?
- [ ] Are dependencies injected or hard-coded with `new`?
- [ ] Is the code reaching through objects? (`a.b.c.d`)
- [ ] Could this be decoupled with an interface?
- [ ] Are there circular dependencies?

## Cohesion Assessment

### Cohesion Types (worst to best)

| Type                | Description                       | Red Flag                                        |
|---------------------|-----------------------------------|-------------------------------------------------|
| **Coincidental**    | Random grouping                   | "Utils", "Helpers", "Common" classes            |
| **Logical**         | Grouped by category, not function | `DataExporter` handling users, orders, products |
| **Temporal**        | Run at same time                  | `Startup` class doing unrelated init            |
| **Procedural**      | Part of same procedure            | Mixed responsibilities in workflow              |
| **Communicational** | Operate on same data              | Good - clear data ownership                     |
| **Functional**      | All contribute to single task     | Best - focused responsibility                   |

### Cohesion Red Flags in Code Review

- [ ] Does every method use instance state?
- [ ] Can the class be described in one sentence without "and"?
- [ ] Would changing one feature require changing unrelated code?
- [ ] Are there logical groupings within the class that could be extracted?

## Anti-Patterns to Recognize

| Anti-Pattern               | Problem                                  | Better Approach                   |
|----------------------------|------------------------------------------|-----------------------------------|
| **God Object**             | One class does everything                | Split by responsibility           |
| **Anemic Domain**          | Data classes + separate logic            | Rich domain objects with behavior |
| **Golden Hammer**          | Using one pattern everywhere             | Choose pattern per context        |
| **Premature Abstraction**  | Abstracting before needed                | Wait for duplication (Rule of 3)  |
| **Speculative Generality** | Building for hypothetical futures        | YAGNI - build what's needed       |
| **Lava Flow**              | Dead code nobody dares remove            | Delete unused code                |
| **Boat Anchor**            | Keeping unused components "just in case" | Remove or document clearly        |

## Review Output Format

When reporting design issues:

```markdown
## Design Assessment Summary

### Critical Issues (blocking)

1. **[Issue Type]** in `file:line`
    - Problem: [What's wrong]
    - Impact: [Why it matters]
    - Suggestion: [How to fix]

### Design Concerns (non-blocking)

- [Concern 1]
- [Concern 2]

### Positive Patterns Observed

- [Good practice found]
```

## Additional Resources

For detailed explanations and examples:

- **`references/coupling-cohesion.md`** - Detailed coupling/cohesion types with code examples
- **`references/code-smells.md`** - Extended code smell catalog with refactoring suggestions

### Related Skills

When fixing identified issues, consult the **design-patterns** skill for:

- SOLID principles (how to fix violations)
- GoF design patterns (solutions to common problems)
- DDD patterns (domain modeling)
- Dependency injection patterns
