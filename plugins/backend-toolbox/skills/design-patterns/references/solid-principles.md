# SOLID Principles - Detailed Reference

This reference covers the SOLID principles, common violation signals, and refactoring approaches for maintainable designs.

## Single Responsibility Principle (SRP)

> "A class should have only one reason to change." — Robert C. Martin

### The Principle

Every module, class, or function should have responsibility over a single part of the functionality. That responsibility should be entirely encapsulated by the class.

### Identifying Violations

**Code smells:**

- Class has multiple unrelated methods
- Changes to different features require modifying the same class
- Class has dependencies for unrelated concerns (e.g., database AND email AND logging)
- Difficulty naming the class without using "And" or "Manager"

**Example violation:**

```typescript
// BAD: User class handles persistence, validation, AND notification
class User {
  constructor(public name: string, public email: string) {}

  validate(): boolean {
    return this.email.includes("@") && this.name.length > 0;
  }

  save(): void {
    // SQL insertion logic
    db.query(
      `INSERT INTO users (name, email) VALUES ('${this.name}', '${this.email}')`
    );
  }

  sendWelcomeEmail(): void {
    // Email sending logic
    emailService.send(this.email, "Welcome!", "Thanks for joining");
  }
}
```

**Refactored:**

```typescript
// GOOD: Separate responsibilities into focused classes
class User {
  constructor(public name: string, public email: string) {}
}

class UserValidator {
  validate(user: User): boolean {
    return user.email.includes("@") && user.name.length > 0;
  }
}

class UserRepository {
  save(user: User): void {
    db.query("INSERT INTO users (name, email) VALUES (?, ?)", [
      user.name,
      user.email,
    ]);
  }
}

class WelcomeEmailSender {
  send(user: User): void {
    emailService.send(user.email, "Welcome!", "Thanks for joining");
  }
}
```

### Applying SRP

1. **Identify reasons for change** - List what business requirements could cause the class to change
2. **Group related functionality** - Methods that change together belong together
3. **Extract classes** - Create new classes for each distinct responsibility
4. **Use composition** - Coordinate multiple classes from a higher level

### Common Pitfalls

- **Over-application**: Don't create a class for every single method
- **Anemic domain**: Don't strip all behavior from domain objects
- **Balance**: A class CAN have multiple methods if they all serve ONE responsibility

---

## Open/Closed Principle (OCP)

> "Software entities should be open for extension, but closed for modification."

### The Principle

Design modules that can have their behavior extended without modifying their source code. New functionality should be added by writing new code, not changing existing code.

### Identifying Violations

**Code smells:**

- Adding a new type requires modifying existing switch/if statements
- Core logic contains conditionals for specific cases
- Changes ripple through the codebase

**Example violation:**

```typescript
// BAD: Adding a new shape requires modifying this function
function calculateArea(shape: Shape): number {
  if (shape.type === "circle") {
    return Math.PI * shape.radius ** 2;
  } else if (shape.type === "rectangle") {
    return shape.width * shape.height;
  } else if (shape.type === "triangle") {
    return (shape.base * shape.height) / 2;
  }
  // Must modify this function for every new shape!
  throw new Error("Unknown shape");
}
```

**Refactored:**

```typescript
// GOOD: New shapes extend without modification
interface Shape {
  calculateArea(): number;
}

class Circle implements Shape {
  constructor(private radius: number) {}
  calculateArea(): number {
    return Math.PI * this.radius ** 2;
  }
}

class Rectangle implements Shape {
  constructor(private width: number, private height: number) {}
  calculateArea(): number {
    return this.width * this.height;
  }
}

// Adding Triangle doesn't modify existing code
class Triangle implements Shape {
  constructor(private base: number, private height: number) {}
  calculateArea(): number {
    return (this.base * this.height) / 2;
  }
}

function calculateArea(shape: Shape): number {
  return shape.calculateArea(); // Works for all shapes, past and future
}
```

### Techniques for OCP

1. **Polymorphism** - Define interfaces, let implementations vary
2. **Strategy Pattern** - Encapsulate algorithms, swap at runtime
3. **Decorator Pattern** - Add behavior by wrapping
4. **Plugin Architecture** - Load extensions dynamically

### When to Apply

- Apply when you see patterns of change (3rd similar modification)
- Don't pre-optimize - wait for actual extension needs
- Balance against YAGNI - speculative generality is also harmful

---

## Liskov Substitution Principle (LSP)

> "Objects of a superclass should be replaceable with objects of subclasses without affecting correctness."

### The Principle

If S is a subtype of T, then objects of type T can be replaced with objects of type S without altering any desirable properties of the program. Subtypes must honor the contracts of their base types.

### Identifying Violations

**Code smells:**

- Subclass throws `NotImplementedException` for inherited methods
- Subclass overrides method to do nothing or behave completely differently
- Code checks type before calling methods (`instanceof`, type guards)
- Subclass violates base class invariants

**Example violation:**

```typescript
// BAD: Square violates Rectangle's contract
class Rectangle {
  constructor(protected width: number, protected height: number) {}

  setWidth(w: number): void {
    this.width = w;
  }
  setHeight(h: number): void {
    this.height = h;
  }
  getArea(): number {
    return this.width * this.height;
  }
}

class Square extends Rectangle {
  setWidth(w: number): void {
    this.width = w;
    this.height = w; // Violates expectation that setWidth only changes width
  }
  setHeight(h: number): void {
    this.width = h;
    this.height = h;
  }
}

// This test passes for Rectangle but fails for Square
function testRectangle(rect: Rectangle): void {
  rect.setWidth(5);
  rect.setHeight(4);
  assert(rect.getArea() === 20); // Fails for Square! (returns 16)
}
```

**Refactored:**

```typescript
// GOOD: Separate abstractions, no inheritance
interface Shape {
  getArea(): number;
}

class Rectangle implements Shape {
  constructor(private width: number, private height: number) {}
  getArea(): number {
    return this.width * this.height;
  }
}

class Square implements Shape {
  constructor(private side: number) {}
  getArea(): number {
    return this.side ** 2;
  }
}
```

### LSP Contract Rules

Subtypes must:

1. **Preconditions** - Cannot strengthen (require more than base)
2. **Postconditions** - Cannot weaken (guarantee less than base)
3. **Invariants** - Must maintain all base class invariants
4. **History constraint** - Cannot modify state in unexpected ways

### Fixing Violations

- Reconsider the hierarchy - maybe inheritance is wrong
- Use composition instead of inheritance
- Create new abstractions that capture the true relationship
- Extract common interface without forcing inheritance

---

## Interface Segregation Principle (ISP)

> "Clients should not be forced to depend on interfaces they do not use."

### The Principle

Many specific interfaces are better than one general-purpose interface. Split large interfaces into smaller, more focused ones so that clients only need to know about methods relevant to them.

### Identifying Violations

**Code smells:**

- Interfaces with 10+ methods
- Implementing classes leave methods empty or throw `NotImplementedException`
- Changes to interface force changes in unrelated implementers
- "Fat" interfaces that serve multiple clients

**Example violation:**

```typescript
// BAD: One interface forces all methods on all implementers
interface Worker {
  work(): void;
  eat(): void;
  sleep(): void;
  attendMeeting(): void;
  writeReport(): void;
}

class Robot implements Worker {
  work(): void {
    /* OK */
  }
  eat(): void {
    throw new Error("Robots do not eat");
  } // Forced to implement
  sleep(): void {
    throw new Error("Robots do not sleep");
  }
  attendMeeting(): void {
    /* OK */
  }
  writeReport(): void {
    /* OK */
  }
}
```

**Refactored:**

```typescript
// GOOD: Segregated interfaces
interface Workable {
  work(): void;
}

interface Feedable {
  eat(): void;
}

interface Restable {
  sleep(): void;
}

interface Collaborator {
  attendMeeting(): void;
  writeReport(): void;
}

class Human implements Workable, Feedable, Restable, Collaborator {
  work(): void {
    /* ... */
  }
  eat(): void {
    /* ... */
  }
  sleep(): void {
    /* ... */
  }
  attendMeeting(): void {
    /* ... */
  }
  writeReport(): void {
    /* ... */
  }
}

class Robot implements Workable, Collaborator {
  work(): void {
    /* ... */
  }
  attendMeeting(): void {
    /* ... */
  }
  writeReport(): void {
    /* ... */
  }
  // No need to implement eat() or sleep()
}
```

### Applying ISP

1. **Identify clients** - Who uses this interface?
2. **Group by usage** - Which methods does each client need?
3. **Extract interfaces** - Create focused interfaces per client need
4. **Compose** - Classes can implement multiple small interfaces

### Role Interfaces

Design interfaces around client roles:

- `Readable` - for clients that read
- `Writable` - for clients that write
- `Closeable` - for clients that manage lifecycle

---

## Dependency Inversion Principle (DIP)

> "High-level modules should not depend on low-level modules. Both should depend on abstractions."

### The Principle

1. High-level modules should not import from low-level modules. Both should depend on abstractions.
2. Abstractions should not depend on details. Details should depend on abstractions.

### Identifying Violations

**Code smells:**

- High-level business logic imports infrastructure (database, HTTP, file system)
- Classes instantiate dependencies with `new`
- Testing requires real database/network/filesystem
- Changes to storage implementation require changes to business logic

**Example violation:**

```typescript
// BAD: OrderService directly depends on concrete implementations
import { MySQLDatabase } from "./mysql-database";
import { StripePaymentGateway } from "./stripe-gateway";
import { SendGridEmailer } from "./sendgrid-emailer";

class OrderService {
  private db = new MySQLDatabase();
  private payment = new StripePaymentGateway();
  private emailer = new SendGridEmailer();

  createOrder(order: Order): void {
    this.db.save(order);
    this.payment.charge(order.total);
    this.emailer.send(order.customerEmail, "Order confirmed");
  }
}
```

**Refactored:**

```typescript
// GOOD: Depend on abstractions, inject implementations
interface OrderRepository {
  save(order: Order): void;
}

interface PaymentGateway {
  charge(amount: number): void;
}

interface EmailService {
  send(to: string, message: string): void;
}

class OrderService {
  constructor(
    private repository: OrderRepository,
    private payment: PaymentGateway,
    private emailer: EmailService
  ) {}

  createOrder(order: Order): void {
    this.repository.save(order);
    this.payment.charge(order.total);
    this.emailer.send(order.customerEmail, "Order confirmed");
  }
}

// Implementations depend on abstractions
class MySQLOrderRepository implements OrderRepository {
  save(order: Order): void {
    /* MySQL-specific */
  }
}

class StripePaymentGateway implements PaymentGateway {
  charge(amount: number): void {
    /* Stripe-specific */
  }
}

// Easy to test with mocks
class MockOrderRepository implements OrderRepository {
  save(order: Order): void {
    /* In-memory for tests */
  }
}
```

### Dependency Injection Patterns

1. **Constructor Injection** - Pass dependencies through constructor (preferred)
2. **Setter Injection** - Set dependencies after construction
3. **Interface Injection** - Implement interface that accepts dependency
4. **Service Locator** - Ask container for dependencies (less preferred)

### Benefits

- **Testability** - Easy to substitute mocks/stubs
- **Flexibility** - Swap implementations without changing consumers
- **Decoupling** - High-level logic isolated from infrastructure
- **Parallel development** - Teams can work on implementations independently

See `references/dependency-injection.md` for detailed DI patterns and container usage.
