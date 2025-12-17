---
name: refactoring-patterns
description: >
  This skill should be used when the user asks to "refactor code", "improve design",
  "restructure without changing behavior", "extract function", "rename variable",
  "simplify code", "clean up this code", "make this more readable", "reduce
  duplication", "apply SOLID principles", or needs guidance on safe transformation
  techniques. Also triggered by requests to reduce complexity, improve maintainability,
  or apply specific refactoring patterns like extract method, inline variable, move
  function, or replace conditional with polymorphism.
---

# Refactoring Patterns Guide

## Core Principle

**Refactoring changes structure, not behavior.**

Every refactor must:

1. Start with passing tests
2. Make one small change
3. Run tests to verify behavior unchanged
4. Repeat

## Safe Refactoring Process

### Before Starting

- [ ] All tests pass (establish baseline)
- [ ] Understand current behavior from tests and usage
- [ ] Identify what must NOT change (public APIs, contracts)
- [ ] Plan small, reversible steps

### During Refactoring

- [ ] One change at a time
- [ ] Run tests after every step
- [ ] If tests fail, revert immediately
- [ ] Commit working states frequently

### After Completing

- [ ] All tests still pass
- [ ] No behavior changes
- [ ] Code is demonstrably improved

## Common Refactoring Patterns

### Extract Function/Method

**When:** Code block does a distinct thing or is duplicated

```
Before:
  // calculate total
  let sum = 0;
  for (item of items) {
    sum += item.price * item.quantity;
  }

After:
  const sum = calculateTotal(items);

  function calculateTotal(items) {
    return items.reduce((sum, item) =>
      sum + item.price * item.quantity, 0);
  }
```

### Extract Variable

**When:** Complex expression is hard to understand

```
Before:
  if (user.age >= 18 && user.country === 'US' && user.verified)

After:
  const isEligible = user.age >= 18 && user.country === 'US' && user.verified;
  if (isEligible)
```

### Inline Function/Variable

**When:** Abstraction adds no clarity

```
Before:
  function isAdult(age) { return age >= 18; }
  if (isAdult(user.age))

After:
  if (user.age >= 18)
```

### Rename

**When:** Name doesn't describe purpose

```
Before:
  function calc(d) { return d * 0.1; }

After:
  function calculateDiscount(price) { return price * 0.1; }
```

### Move Function/Field

**When:** Function/field belongs to different module

Steps:

1. Copy to new location
2. Update all callers to use new location
3. Run tests
4. Remove from old location
5. Run tests again

### Replace Conditional with Polymorphism

**When:** Switch/if chains based on type

```
Before:
  function getArea(shape) {
    switch (shape.type) {
      case 'circle': return Math.PI * shape.radius ** 2;
      case 'rectangle': return shape.width * shape.height;
    }
  }

After:
  class Circle {
    getArea() { return Math.PI * this.radius ** 2; }
  }
  class Rectangle {
    getArea() { return this.width * this.height; }
  }
```

### Extract Interface

**When:** Multiple implementations share common contract

Steps:

1. Identify common methods/properties
2. Create interface with those signatures
3. Have implementations declare interface
4. Update consumers to use interface type

### Decompose Conditional

**When:** Complex conditional logic

```
Before:
  if (date.before(SUMMER_START) || date.after(SUMMER_END))
    charge = quantity * winterRate + winterServiceCharge;
  else
    charge = quantity * summerRate;

After:
  if (isSummer(date))
    charge = summerCharge(quantity);
  else
    charge = winterCharge(quantity);
```

## Anti-Patterns to Avoid

### Big Bang Refactoring

- Changing many things at once
- Hard to identify what broke tests
- Difficult to revert

### Refactoring Without Tests

- No way to verify behavior unchanged
- High risk of introducing bugs

### Refactoring During Feature Work

- Mixes concerns in commits
- Makes code review harder
- Should be separate commits/PRs

### Gold Plating

- Refactoring beyond what's needed
- Adding features during refactor
- Over-abstracting for hypothetical futures

## Refactoring Scope Decisions

| Scope                       | When Appropriate            |
|-----------------------------|-----------------------------|
| **Local** (within function) | During any work             |
| **Module** (within file)    | Dedicated refactor task     |
| **Cross-module**            | Planned refactor with tests |
| **Architecture**            | Major initiative with team  |

## Additional Resources

### Reference Files

For detailed patterns and techniques, consult:

- **`references/patterns-catalog.md`** - Extended catalog of refactoring patterns with mechanics and multi-language
  examples (Extract Function, Move Method, Replace Conditional with Polymorphism, etc.)
- **`references/code-smells.md`** - Comprehensive guide to identifying code smells (Bloaters, Couplers, Change
  Preventers) and their refactoring solutions

### Working Examples

Before/after examples in `examples/`:

- **`extract-function-before.ts`** / **`extract-function-after.ts`** - Demonstrates extracting focused functions from a
  long method
- **`replace-conditional-polymorphism-before.ts`** / **`replace-conditional-polymorphism-after.ts`** - Shows replacing
  type-based switch statements with polymorphic classes

## Related Skills

When evaluating design quality during refactoring, consult the **software-design-principles** skill for:

- SOLID principles to identify design violations
- Design patterns to guide transformations
- Coupling/cohesion metrics to measure improvement
- Dependency injection patterns for decoupling
