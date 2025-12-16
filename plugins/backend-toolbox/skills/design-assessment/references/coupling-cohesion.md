# Coupling and Cohesion - Detailed Reference

Types, measurement techniques, and refactoring guidance for coupling and cohesion in software design.

## Overview

**Coupling** and **cohesion** are fundamental metrics for evaluating software design quality:

- **Coupling**: Degree of interdependence between modules (AIM FOR LOW)
- **Cohesion**: Degree to which elements within a module belong together (AIM FOR HIGH)

The goal: **High cohesion within modules, low coupling between modules.**

---

## Coupling

### Types of Coupling (Worst to Best)

#### 1. Content Coupling (WORST)

One module modifies or relies on internal workings of another.

```typescript
// TERRIBLE: Directly manipulating another module's internals
class OrderProcessor {
  process(order: Order): void {
    // Directly accessing and modifying inventory internals
    inventory._items[order.productId]._count -= order.quantity;
    inventory._lastModified = new Date();
  }
}
```

**Problems:**

- Changes to Inventory internals break OrderProcessor
- No encapsulation
- Impossible to test in isolation

#### 2. Common Coupling (BAD)

Modules share global data.

```typescript
// BAD: Global state shared between modules
let globalConfig = { taxRate: 0.1, currency: "USD" };

class PriceCalculator {
  calculate(price: number): number {
    return price * (1 + globalConfig.taxRate);
  }
}

class InvoiceGenerator {
  generate(amount: number): string {
    return `${globalConfig.currency} ${amount}`;
  }
}
```

**Problems:**

- Any module can change global state
- Order of operations matters
- Hard to track what changed state
- Difficult to test

#### 3. Control Coupling (POOR)

One module controls another's flow by passing control information.

```typescript
// POOR: Passing flags to control behavior
class ReportGenerator {
  generate(
    data: Data,
    format: "pdf" | "html" | "csv",
    includeHeaders: boolean,
    sortOrder: "asc" | "desc"
  ): Report {
    if (format === "pdf") {
      // PDF logic
    } else if (format === "html") {
      // HTML logic
    } else {
      // CSV logic
    }

    if (includeHeaders) {
      // Add headers
    }

    if (sortOrder === "asc") {
      // Sort ascending
    } else {
      // Sort descending
    }
  }
}
```

**Problems:**

- Caller must understand implementation
- Changes require modifying conditionals
- Hard to extend

**Better approach - Strategy Pattern:**

```typescript
interface ReportFormatter {
  format(data: Data): Report;
}

class PdfFormatter implements ReportFormatter {
  /* ... */
}
class HtmlFormatter implements ReportFormatter {
  /* ... */
}
class CsvFormatter implements ReportFormatter {
  /* ... */
}

class ReportGenerator {
  constructor(private formatter: ReportFormatter) {}

  generate(data: Data): Report {
    return this.formatter.format(data);
  }
}
```

#### 4. Stamp Coupling (FAIR)

Passing entire data structures when only part is needed.

```typescript
// FAIR: Passing entire user when only email needed
class EmailService {
  sendWelcome(user: User): void {
    // Only uses user.email, but receives entire User object
    this.send(user.email, "Welcome!");
  }
}
```

**Problems:**

- Creates unnecessary dependency on User structure
- Changes to User might affect EmailService
- Harder to test (need full User object)

**Better approach:**

```typescript
// GOOD: Only receive what's needed
class EmailService {
  sendWelcome(email: string): void {
    this.send(email, "Welcome!");
  }
}
```

#### 5. Data Coupling (GOOD)

Modules share only necessary data through parameters.

```typescript
// GOOD: Only passing required data
class TaxCalculator {
  calculate(amount: number, taxRate: number): number {
    return amount * taxRate;
  }
}

class ShippingCalculator {
  calculate(weight: number, distance: number): number {
    return weight * 0.5 + distance * 0.1;
  }
}
```

**Benefits:**

- Clear interfaces
- Easy to test
- Changes are localized

#### 6. Message Coupling (BEST)

Modules communicate only through well-defined interfaces/messages.

```typescript
// BEST: Communication through abstract interfaces
interface OrderEvent {
  orderId: string;
  timestamp: Date;
}

interface OrderCreatedEvent extends OrderEvent {
  type: "ORDER_CREATED";
  customerId: string;
  items: OrderItem[];
}

interface EventBus {
  publish(event: OrderEvent): void;
  subscribe(eventType: string, handler: (event: OrderEvent) => void): void;
}

class OrderService {
  constructor(private eventBus: EventBus) {}

  createOrder(order: Order): void {
    // Create order...
    this.eventBus.publish({
      type: "ORDER_CREATED",
      orderId: order.id,
      timestamp: new Date(),
      customerId: order.customerId,
      items: order.items,
    });
  }
}

// Other services subscribe without knowing about OrderService
class InventoryService {
  constructor(eventBus: EventBus) {
    eventBus.subscribe("ORDER_CREATED", this.handleOrderCreated.bind(this));
  }

  private handleOrderCreated(event: OrderCreatedEvent): void {
    // Update inventory...
  }
}
```

**Benefits:**

- Modules don't know about each other
- Easy to add new subscribers
- Highly testable

---

### Measuring Coupling

#### Afferent Coupling (Ca)

Number of classes that depend on this class.

- High Ca = Many dependents = Changes are risky
- Classes with high Ca should be stable

#### Efferent Coupling (Ce)

Number of classes this class depends on.

- High Ce = Depends on many = Sensitive to changes
- Classes with high Ce are fragile

#### Instability (I)

```
I = Ce / (Ca + Ce)
```

- I = 0: Maximally stable (many dependents, few dependencies)
- I = 1: Maximally unstable (few dependents, many dependencies)

**Goal:** Dependencies should flow toward stability.

---

### Reducing Coupling

#### 1. Use Dependency Injection

```typescript
// Instead of:
class OrderService {
  private repo = new MySQLOrderRepository();
}

// Use:
class OrderService {
  constructor(private repo: OrderRepository) {}
}
```

#### 2. Define Clear Interfaces

```typescript
// Define contracts, not implementations
interface PaymentGateway {
  charge(amount: number): Promise<PaymentResult>;
  refund(transactionId: string): Promise<RefundResult>;
}
```

#### 3. Apply Law of Demeter

Only talk to immediate friends:

```typescript
// BAD: Reaching through objects
order.getCustomer().getAddress().getCity();

// GOOD: Ask, don't reach
order.getShippingCity();
```

#### 4. Use Events for Cross-Cutting Concerns

```typescript
// Instead of direct calls
orderService.createOrder(order);
inventoryService.update(order);
emailService.sendConfirmation(order);
analyticsService.track(order);

// Use events
orderService.createOrder(order); // Publishes ORDER_CREATED
// Other services subscribe to ORDER_CREATED
```

---

## Cohesion

### Types of Cohesion (Worst to Best)

#### 1. Coincidental Cohesion (WORST)

Elements are grouped arbitrarily with no meaningful relationship.

```typescript
// TERRIBLE: Random utilities thrown together
class Utils {
  static formatDate(date: Date): string {
    /* ... */
  }
  static calculateTax(amount: number): number {
    /* ... */
  }
  static validateEmail(email: string): boolean {
    /* ... */
  }
  static compressImage(image: Buffer): Buffer {
    /* ... */
  }
  static sendNotification(message: string): void {
    /* ... */
  }
}
```

**Problems:**

- No logical organization
- Hard to find functionality
- Changes affect unrelated code

#### 2. Logical Cohesion (POOR)

Elements are grouped because they do similar things, but operate on different data.

```typescript
// POOR: Grouped by "type" of operation
class DataExporter {
  exportUsersToCsv(users: User[]): string {
    /* ... */
  }
  exportOrdersToXml(orders: Order[]): string {
    /* ... */
  }
  exportProductsToJson(products: Product[]): string {
    /* ... */
  }
}
```

**Problems:**

- Different data types handled by same class
- Changes to one export affect others

#### 3. Temporal Cohesion (POOR)

Elements are grouped because they're executed at the same time.

```typescript
// POOR: Grouped by "when" they run
class StartupInitializer {
  initialize(): void {
    this.loadConfiguration();
    this.connectDatabase();
    this.initializeCache();
    this.startScheduler();
    this.warmUpConnections();
    this.registerMetrics();
  }
}
```

**Problems:**

- Unrelated responsibilities
- Hard to test individually
- Changes to one area affect others

#### 4. Procedural Cohesion (FAIR)

Elements are grouped because they follow a specific sequence.

```typescript
// FAIR: Steps in a process
class OrderProcessor {
  process(order: Order): void {
    this.validateOrder(order);
    this.calculateTotals(order);
    this.applyDiscounts(order);
    this.processPayment(order);
    this.updateInventory(order);
    this.sendConfirmation(order);
  }
}
```

**Better than temporal**, but still mixes different responsibilities.

#### 5. Communicational Cohesion (GOOD)

Elements operate on the same data.

```typescript
// GOOD: All methods work with User data
class UserService {
  create(userData: CreateUserDto): User {
    /* ... */
  }
  update(id: string, userData: UpdateUserDto): User {
    /* ... */
  }
  delete(id: string): void {
    /* ... */
  }
  findById(id: string): User | null {
    /* ... */
  }
  findByEmail(email: string): User | null {
    /* ... */
  }
}
```

**Benefits:**

- Clear data ownership
- Related operations together
- Easier to understand

#### 6. Sequential Cohesion (GOOD)

Output of one element is input to the next.

```typescript
// GOOD: Pipeline processing
class ImageProcessor {
  process(image: RawImage): ProcessedImage {
    const decoded = this.decode(image);
    const resized = this.resize(decoded);
    const filtered = this.applyFilters(resized);
    const compressed = this.compress(filtered);
    return compressed;
  }
}
```

**Benefits:**

- Clear data flow
- Easy to understand transformation
- Can be parallelized

#### 7. Functional Cohesion (BEST)

All elements contribute to a single, well-defined task.

```typescript
// BEST: Single, focused responsibility
class PasswordHasher {
  private readonly saltRounds = 12;

  async hash(password: string): Promise<string> {
    return bcrypt.hash(password, this.saltRounds);
  }

  async verify(password: string, hash: string): Promise<boolean> {
    return bcrypt.compare(password, hash);
  }
}

class EmailValidator {
  private readonly emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  isValid(email: string): boolean {
    return this.emailRegex.test(email);
  }

  normalize(email: string): string {
    return email.toLowerCase().trim();
  }
}
```

**Benefits:**

- Single responsibility
- Highly reusable
- Easy to test
- Easy to understand

---

### Measuring Cohesion

#### Lack of Cohesion in Methods (LCOM)

Measures how related methods are within a class.

**LCOM1:** Count method pairs that don't share instance variables minus pairs that do.

- LCOM1 = 0: Cohesive
- LCOM1 > 0: Lack of cohesion

**LCOM4 (Preferred):** Count connected components in method-field graph.

- LCOM4 = 1: Cohesive (all methods connected)
- LCOM4 > 1: Should potentially be split into multiple classes

#### Signs of Low Cohesion

- Class has methods that don't use class fields
- Class has unrelated groups of methods
- Difficult to name the class (uses "Manager", "Helper", "Utils")
- Class changes for multiple unrelated reasons

---

### Increasing Cohesion

#### 1. Single Responsibility

Extract classes when responsibilities diverge:

```typescript
// Before: Mixed responsibilities
class User {
  save(): void {
    /* database logic */
  }
  sendEmail(): void {
    /* email logic */
  }
  validate(): boolean {
    /* validation logic */
  }
}

// After: Separated responsibilities
class User {
  /* just data */
}
class UserRepository {
  save(user: User): void {
    /* ... */
  }
}
class UserEmailService {
  sendWelcome(user: User): void {
    /* ... */
  }
}
class UserValidator {
  validate(user: User): ValidationResult {
    /* ... */
  }
}
```

#### 2. Group Related Data and Behavior

```typescript
// Before: Data and behavior separated
interface Address {
  street: string;
  city: string;
  country: string;
  postalCode: string;
}

function formatAddress(address: Address): string {
  /* ... */
}
function validateAddress(address: Address): boolean {
  /* ... */
}

// After: Data and behavior together
class Address {
  constructor(
    public street: string,
    public city: string,
    public country: string,
    public postalCode: string
  ) {}

  format(): string {
    /* ... */
  }
  validate(): boolean {
    /* ... */
  }
}
```

#### 3. Extract Value Objects

```typescript
// Before: Primitive obsession
class Order {
  private amount: number;
  private currency: string;

  convertTo(targetCurrency: string): void {
    // Currency conversion logic mixed with order
  }
}

// After: Value object
class Money {
  constructor(private amount: number, private currency: Currency) {}

  convertTo(targetCurrency: Currency): Money {
    // Focused currency conversion
  }

  add(other: Money): Money {
    /* ... */
  }
  multiply(factor: number): Money {
    /* ... */
  }
}

class Order {
  constructor(private total: Money) {}
}
```

---

## Applying in Practice

### Code Review Checklist

**Coupling Questions:**

- [ ] Does this change introduce new dependencies?
- [ ] Are dependencies injected or hard-coded?
- [ ] Is the module reaching through objects (Law of Demeter)?
- [ ] Could this be decoupled with an interface?

**Cohesion Questions:**

- [ ] Does every method use instance state?
- [ ] Can the class be described in one sentence?
- [ ] Would changing one feature require changing unrelated code?
- [ ] Are there logical groupings within the class?

### Refactoring Triggers

**Split class when:**

- Two groups of methods never interact
- Class has multiple reasons to change
- Methods use different subsets of fields

**Extract interface when:**

- Multiple implementations exist or are likely
- Testing requires mocking
- Module should be swappable

**Use events when:**

- Multiple systems react to the same change
- Ordering doesn't matter
- Cross-cutting concerns (logging, analytics)
