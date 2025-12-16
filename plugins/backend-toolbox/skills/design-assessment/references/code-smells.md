# Code Smells - Detailed Reference

This reference is used for identifying and communicating common code smells during design assessment.
Code smells are used as indicators of potential problems in code design. Code correctness is not necessarily implied,
but areas worth investigating are suggested.

## Bloaters

Code that has grown too large to be easily understood or maintained.

### Long Method

**Signs:**

- Method exceeds 20-30 lines
- Multiple levels of abstraction in one method
- Comments separating "sections" of the method
- Difficult to name the method concisely

**Example (problematic):**

```typescript
function processOrder(order: Order): void {
  // Validate order
  if (!order.customerId) throw new Error("Missing customer");
  if (order.items.length === 0) throw new Error("Empty order");
  for (const item of order.items) {
    if (item.quantity <= 0) throw new Error("Invalid quantity");
  }

  // Calculate totals
  let subtotal = 0;
  for (const item of order.items) {
    subtotal += item.price * item.quantity;
  }
  const tax = subtotal * 0.1;
  const total = subtotal + tax;

  // Apply discounts
  let discount = 0;
  if (total > 100) discount = total * 0.05;
  if (order.isVip) discount += total * 0.1;

  // Save to database
  db.orders.insert({
    ...order,
    subtotal,
    tax,
    discount,
    total: total - discount,
  });

  // Send notifications
  emailService.send(order.customerEmail, "Order confirmed");
  if (order.isGift) emailService.send(order.giftRecipientEmail, "Gift coming");
}
```

**Refactored:**

```typescript
function processOrder(order: Order): void {
  validateOrder(order);
  const pricing = calculatePricing(order);
  saveOrder(order, pricing);
  sendNotifications(order);
}
```

### Large Class

**Signs:**

- Class exceeds 200-300 lines
- Many unrelated methods grouped together
- Multiple distinct responsibilities
- Hard to name without generic terms (Manager, Handler, Processor)

**Refactoring:** Extract classes by responsibility. Group related methods and fields into focused classes.

### Long Parameter List

**Signs:**

- More than 3-4 parameters
- Parameters often passed together
- Boolean flags controlling behavior

**Example (problematic):**

```typescript
function createUser(
  name: string,
  email: string,
  age: number,
  street: string,
  city: string,
  country: string,
  postalCode: string,
  isAdmin: boolean,
  sendWelcomeEmail: boolean
): User;
```

**Refactored:**

```typescript
interface CreateUserDto {
  name: string;
  email: string;
  age: number;
  address: Address;
}

interface CreateUserOptions {
  isAdmin?: boolean;
  sendWelcomeEmail?: boolean;
}

function createUser(data: CreateUserDto, options?: CreateUserOptions): User;
```

### Primitive Obsession

**Signs:**

- Using strings for structured data (emails, phone numbers, IDs)
- Validation scattered throughout codebase
- Magic numbers/strings
- Arrays or tuples instead of objects

**Example (problematic):**

```typescript
function sendEmail(to: string, subject: string): void {
  if (!to.includes("@")) throw new Error("Invalid email");
  // ...
}

// Validation repeated everywhere email is used
```

**Refactored:**

```typescript
class Email {
  constructor(public readonly value: string) {
    if (!value.includes("@")) throw new Error("Invalid email");
  }
}

function sendEmail(to: Email, subject: string): void {
  // Email is guaranteed valid
}
```

### Data Clumps

**Signs:**

- Same group of parameters appear in multiple functions
- Same fields appear together in multiple classes
- Extracting one field from the group doesn't make sense

**Example (problematic):**

```typescript
function calculateDistance(
  x1: number,
  y1: number,
  x2: number,
  y2: number
): number;
function drawLine(x1: number, y1: number, x2: number, y2: number): void;
function isWithinBounds(
  x: number,
  y: number,
  maxX: number,
  maxY: number
): boolean;
```

**Refactored:**

```typescript
class Point {
  constructor(public x: number, public y: number) {}
}

function calculateDistance(from: Point, to: Point): number;
function drawLine(from: Point, to: Point): void;
function isWithinBounds(point: Point, bounds: Point): boolean;
```

---

## Object-Orientation Abusers

Incorrect or incomplete application of OO principles.

### Switch Statements (Type-based)

**Signs:**

- Switch/if-chain based on type field
- Same switch appears in multiple places
- Adding new type requires modifying multiple functions

**Example (problematic):**

```typescript
function calculatePay(employee: Employee): number {
  switch (employee.type) {
    case "hourly":
      return employee.hours * employee.rate;
    case "salaried":
      return employee.salary / 12;
    case "commissioned":
      return employee.sales * employee.commission;
  }
}

function getTitle(employee: Employee): string {
  switch (employee.type) {
    case "hourly":
      return "Hourly Worker";
    case "salaried":
      return "Salaried Employee";
    case "commissioned":
      return "Sales Representative";
  }
}
```

**Refactored:**

```typescript
interface Employee {
  calculatePay(): number;
  getTitle(): string;
}

class HourlyEmployee implements Employee {
  calculatePay(): number {
    return this.hours * this.rate;
  }
  getTitle(): string {
    return "Hourly Worker";
  }
}

class SalariedEmployee implements Employee {
  calculatePay(): number {
    return this.salary / 12;
  }
  getTitle(): string {
    return "Salaried Employee";
  }
}
```

### Refused Bequest

**Signs:**

- Subclass doesn't use most inherited methods
- Subclass overrides methods to throw exceptions
- Subclass overrides methods to do nothing

**Example (problematic):**

```typescript
class Bird {
  fly(): void {
    /* flying logic */
  }
  eat(): void {
    /* eating logic */
  }
}

class Penguin extends Bird {
  fly(): void {
    throw new Error("Penguins cannot fly"); // Refused bequest
  }
}
```

**Refactored:**

```typescript
interface Bird {
  eat(): void;
}

interface FlyingBird extends Bird {
  fly(): void;
}

class Sparrow implements FlyingBird {
  fly(): void {
    /* ... */
  }
  eat(): void {
    /* ... */
  }
}

class Penguin implements Bird {
  eat(): void {
    /* ... */
  }
  // No fly() method to refuse
}
```

---

## Change Preventers

Code structures that make changes difficult.

### Divergent Change

**Signs:**

- One class needs to be changed for many different reasons
- Different developers frequently editing the same class for unrelated features
- Class name is vague (Handler, Manager, Service without clear scope)

**Problem:** Violates Single Responsibility Principle.

**Example:** A `UserService` class that handles authentication, profile updates, notification preferences, and billing -
each feature change touches this one class.

**Refactoring:** Split into `AuthenticationService`, `ProfileService`, `NotificationPreferences`, `BillingService`.

### Shotgun Surgery

**Signs:**

- Making one logical change requires editing many classes
- Same kind of edit repeated in multiple places
- Cross-cutting concerns scattered throughout codebase

**Problem:** Related logic is scattered, leading to missed updates and inconsistencies.

**Example:** Adding a new field to an entity requires updating the entity, DTO, mapper, validator, repository, API
controller, and tests - all with similar boilerplate.

**Refactoring:**

- Centralize the logic using patterns like Strategy or Template Method
- Use code generation or reflection for repetitive mappings
- Consider AOP for cross-cutting concerns

---

## Couplers

Excessive coupling between classes.

### Feature Envy

**Signs:**

- Method uses another class's data more than its own
- Lots of getter calls on another object
- Method would fit better in the other class

**Example (problematic):**

```typescript
class OrderPrinter {
  print(order: Order): string {
    // Uses Order's data extensively
    return `
      Customer: ${order.getCustomer().getName()}
      Items: ${order
        .getItems()
        .map((i) => i.getName())
        .join(", ")}
      Total: ${order.getItems().reduce((sum, i) => sum + i.getPrice(), 0)}
      Address: ${order.getCustomer().getAddress().format()}
    `;
  }
}
```

**Refactored:**

```typescript
class Order {
  format(): string {
    // Order formats itself
    return `
      Customer: ${this.customer.name}
      Items: ${this.items.map((i) => i.name).join(", ")}
      Total: ${this.total}
      Address: ${this.customer.address.format()}
    `;
  }
}
```

### Message Chains

**Signs:**

- Long chains of method calls: `a.getB().getC().getD()`
- Navigating deep into object graphs
- Changes to intermediate objects break the chain

**Problem:** Violates Law of Demeter ("only talk to immediate friends").

**Example (problematic):**

```typescript
const city = order.getCustomer().getAddress().getCity();
```

**Refactored:**

```typescript
// Option 1: Delegate method
const city = order.getShippingCity();

// Option 2: Pass what's needed
function processOrder(city: string) {
  /* ... */
}
processOrder(order.shippingCity);
```

### Inappropriate Intimacy

**Signs:**

- Classes access each other's private/internal fields
- Bidirectional dependencies between classes
- Classes that are always changed together

**Refactoring:**

- Move methods/fields to reduce coupling
- Extract a new class for shared behavior
- Replace bidirectional with unidirectional association

### Middle Man

**Signs:**

- Class delegates most methods to another class
- Wrapper adds little value
- Clients would be better off talking directly to the delegate

**Example (problematic):**

```typescript
class PersonWrapper {
  constructor(private person: Person) {}
  getName(): string {
    return this.person.getName();
  }
  getAge(): number {
    return this.person.getAge();
  }
  getAddress(): Address {
    return this.person.getAddress();
  }
  // Just forwarding everything...
}
```

**Refactoring:** Remove the middle man and use the delegate directly, unless the wrapper provides real value (like lazy
loading, access control, or adapting interfaces).

---

## Dispensables

Code that serves no purpose and should be removed.

### Dead Code

**Signs:**

- Unreachable code after return/throw
- Unused variables, parameters, or methods
- Commented-out code
- Code handling impossible conditions

**Action:** Delete it. Version control preserves history if needed.

### Speculative Generality

**Signs:**

- Unused interfaces, abstract classes, or parameters
- "Hooks" for future extension that are never used
- Complex inheritance hierarchies for single implementation
- Parameters that always receive the same value

**Refactoring:** Remove unused abstractions. Add them when actually needed.

### Duplicate Code

**Signs:**

- Copy-pasted logic
- Similar code blocks with minor variations
- Same bug fixed in multiple places

**Refactoring:**

- Extract method for identical code
- Extract method with parameters for similar code
- Pull up to parent class for sibling duplication
- Extract utility class for unrelated duplicates

---

## Smell Prioritization

When reviewing code, prioritize smells by impact:

| Priority   | Smells                               | Why                    |
|------------|--------------------------------------|------------------------|
| **High**   | Shotgun Surgery, Divergent Change    | Make all changes risky |
| **High**   | Feature Envy, Inappropriate Intimacy | Create tight coupling  |
| **Medium** | Long Method, Large Class             | Reduce comprehension   |
| **Medium** | Switch Statements (type-based)       | Violate OCP            |
| **Low**    | Long Parameter List, Data Clumps     | Minor friction         |
| **Low**    | Dead Code, Comments                  | Noise but not harmful  |

## When NOT to Refactor Smells

- **Working code under time pressure** - Fix smells when you're changing the area anyway
- **Code scheduled for replacement** - Don't polish code that's being deprecated
- **Performance-critical code** - Some "smells" are intentional optimizations
- **Unfamiliar codebase** - Understand before changing
