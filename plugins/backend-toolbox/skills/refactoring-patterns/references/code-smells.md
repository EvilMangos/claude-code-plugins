# Code Smells Guide

Comprehensive guide to identifying code smells and their corresponding refactoring solutions.

## Bloaters

Code that has grown too large and unwieldy.

### Long Method

**Symptoms:**

- Method spans more than 20-30 lines
- Multiple levels of abstraction mixed together
- Comments needed to explain sections
- Scrolling required to see entire method

**Refactorings:**

- **Extract Function** - Pull out cohesive blocks
- **Replace Temp with Query** - Remove temporary variables
- **Introduce Parameter Object** - Reduce parameter count
- **Decompose Conditional** - Extract complex conditions

**Example:**

```typescript
// Smell: Long method with mixed concerns
function processOrder(order: Order) {
  // Validate order
  if (!order.items || order.items.length === 0) {
    throw new Error('Order has no items');
  }
  if (!order.customer) {
    throw new Error('Order has no customer');
  }

  // Calculate totals
  let subtotal = 0;
  for (const item of order.items) {
    subtotal += item.price * item.quantity;
  }

  // Apply discounts
  let discount = 0;
  if (order.customer.isVIP) {
    discount = subtotal * 0.1;
  }
  if (order.promoCode === 'SAVE20') {
    discount += subtotal * 0.2;
  }

  // Calculate shipping
  let shipping = 0;
  if (order.shippingMethod === 'express') {
    shipping = 25;
  } else if (order.shippingMethod === 'overnight') {
    shipping = 50;
  } else {
    shipping = subtotal > 100 ? 0 : 10;
  }

  // ... continues for 50 more lines
}

// Better: Extract into focused functions
function processOrder(order: Order): ProcessedOrder {
  validateOrder(order);
  const subtotal = calculateSubtotal(order.items);
  const discount = calculateDiscount(order, subtotal);
  const shipping = calculateShipping(order, subtotal);
  return createProcessedOrder(order, subtotal, discount, shipping);
}
```

### Large Class

**Symptoms:**

- Class has many instance variables (>7-10)
- Class has many methods (>15-20)
- Class name includes "Manager", "Processor", "Handler" doing many things
- Changes to class for multiple unrelated reasons

**Refactorings:**

- **Extract Class** - Create new class for subset of fields/methods
- **Extract Subclass** - When variations suggest inheritance
- **Extract Interface** - Define contracts for groups of methods

**Example:**

```typescript
// Smell: Class doing too many things
class UserManager {
  // User CRUD
  createUser() { }
  updateUser() { }
  deleteUser() { }

  // Authentication
  login() { }
  logout() { }
  resetPassword() { }

  // Email
  sendWelcomeEmail() { }
  sendPasswordReset() { }

  // Reporting
  generateUserReport() { }
  getUserStats() { }
}

// Better: Split by responsibility
class UserRepository {
  create() { }
  update() { }
  delete() { }
}

class AuthenticationService {
  login() { }
  logout() { }
  resetPassword() { }
}

class UserEmailService {
  sendWelcome() { }
  sendPasswordReset() { }
}

class UserReportingService {
  generateReport() { }
  getStats() { }
}
```

### Long Parameter List

**Symptoms:**

- Function takes more than 3-4 parameters
- Parameters are often passed together as a group
- Adding new features requires adding more parameters

**Refactorings:**

- **Introduce Parameter Object** - Group related parameters
- **Preserve Whole Object** - Pass object instead of extracting values
- **Replace Parameter with Query** - Let function get value itself

**Example:**

```typescript
// Smell: Too many parameters
function createUser(
  firstName: string,
  lastName: string,
  email: string,
  phone: string,
  street: string,
  city: string,
  state: string,
  zip: string,
  country: string
) { }

// Better: Parameter objects
interface UserName {
  first: string;
  last: string;
}

interface ContactInfo {
  email: string;
  phone: string;
}

interface Address {
  street: string;
  city: string;
  state: string;
  zip: string;
  country: string;
}

function createUser(name: UserName, contact: ContactInfo, address: Address) { }
```

### Primitive Obsession

**Symptoms:**

- Using primitives for domain concepts (string for email, number for money)
- Validation logic scattered across codebase
- Special values have implicit meaning (status = 1 means "active")

**Refactorings:**

- **Replace Primitive with Object** - Create value objects
- **Replace Type Code with Subclasses** - Use polymorphism
- **Replace Type Code with State/Strategy** - Use patterns

**Example:**

```typescript
// Smell: Primitives everywhere
function createTransaction(
  amount: number,       // What currency?
  from: string,         // Account ID? Name?
  to: string,
  date: string,         // What format?
  status: number        // What do values mean?
) { }

// Better: Value objects
class Money {
  constructor(
    private amount: number,
    private currency: Currency
  ) {
    if (amount < 0) throw new Error('Amount cannot be negative');
  }

  add(other: Money): Money {
    if (this.currency !== other.currency) {
      throw new Error('Cannot add different currencies');
    }
    return new Money(this.amount + other.amount, this.currency);
  }
}

class AccountId {
  constructor(private value: string) {
    if (!AccountId.isValid(value)) {
      throw new Error('Invalid account ID');
    }
  }

  static isValid(value: string): boolean {
    return /^[A-Z]{2}\d{10}$/.test(value);
  }
}

enum TransactionStatus {
  Pending = 'PENDING',
  Completed = 'COMPLETED',
  Failed = 'FAILED'
}

function createTransaction(
  amount: Money,
  from: AccountId,
  to: AccountId,
  date: Date,
  status: TransactionStatus
) { }
```

### Data Clumps

**Symptoms:**

- Same group of fields appears in multiple classes
- Same group of parameters appears in multiple functions
- Changing one field often requires changing others in the group

**Refactorings:**

- **Extract Class** - Create class for the clump
- **Introduce Parameter Object** - Group parameters

**Example:**

```typescript
// Smell: Same fields appear together
class Customer {
  name: string;
  street: string;
  city: string;
  state: string;
  zip: string;
}

class Order {
  shippingStreet: string;
  shippingCity: string;
  shippingState: string;
  shippingZip: string;

  billingStreet: string;
  billingCity: string;
  billingState: string;
  billingZip: string;
}

// Better: Extract Address class
class Address {
  constructor(
    public street: string,
    public city: string,
    public state: string,
    public zip: string
  ) { }
}

class Customer {
  name: string;
  address: Address;
}

class Order {
  shippingAddress: Address;
  billingAddress: Address;
}
```

## Object-Orientation Abusers

Code that doesn't properly use OO features.

### Switch Statements

**Symptoms:**

- Switch or if-else chains based on type/status
- Same switch appears in multiple places
- Adding new type requires changes in many places

**Refactorings:**

- **Replace Conditional with Polymorphism**
- **Replace Type Code with Subclasses**
- **Replace Type Code with State/Strategy**

**Example:**

```typescript
// Smell: Type-based switch
function calculateArea(shape: Shape): number {
  switch (shape.type) {
    case 'circle':
      return Math.PI * shape.radius ** 2;
    case 'rectangle':
      return shape.width * shape.height;
    case 'triangle':
      return 0.5 * shape.base * shape.height;
    default:
      throw new Error('Unknown shape');
  }
}

// Better: Polymorphism
interface Shape {
  calculateArea(): number;
}

class Circle implements Shape {
  constructor(private radius: number) { }
  calculateArea(): number {
    return Math.PI * this.radius ** 2;
  }
}

class Rectangle implements Shape {
  constructor(private width: number, private height: number) { }
  calculateArea(): number {
    return this.width * this.height;
  }
}
```

### Refused Bequest

**Symptoms:**

- Subclass doesn't use most inherited methods
- Subclass overrides methods to throw exceptions
- Subclass ignores or disables parent behavior

**Refactorings:**

- **Replace Superclass with Delegate** - Use composition
- **Push Down Method/Field** - Move to subclasses that need it
- **Extract Superclass** - Create new common parent

**Example:**

```typescript
// Smell: Bird that can't fly
class Bird {
  fly() { }
  eat() { }
  sleep() { }
}

class Penguin extends Bird {
  fly() {
    throw new Error("Penguins can't fly!"); // Violates LSP
  }
}

// Better: Split the hierarchy
interface Animal {
  eat(): void;
  sleep(): void;
}

interface FlyingAnimal extends Animal {
  fly(): void;
}

class Sparrow implements FlyingAnimal {
  fly() { }
  eat() { }
  sleep() { }
}

class Penguin implements Animal {
  eat() { }
  sleep() { }
  swim() { }
}
```

### Parallel Inheritance Hierarchies

**Symptoms:**

- Creating a subclass in one hierarchy requires creating one in another
- Two hierarchies mirror each other
- Changes in one hierarchy require changes in the other

**Refactorings:**

- **Move Method/Field** - Consolidate into single hierarchy
- **Replace Inheritance with Delegation**

**Example:**

```typescript
// Smell: Parallel hierarchies
class Employee { }
class Engineer extends Employee { }
class Salesperson extends Employee { }

class EmployeeReport { }
class EngineerReport extends EmployeeReport { }  // Mirrors Employee hierarchy
class SalespersonReport extends EmployeeReport { }

// Better: Strategy pattern
interface ReportStrategy {
  generateReport(employee: Employee): Report;
}

class EngineerReportStrategy implements ReportStrategy {
  generateReport(employee: Engineer): Report { }
}

class Employee {
  constructor(private reportStrategy: ReportStrategy) { }

  generateReport(): Report {
    return this.reportStrategy.generateReport(this);
  }
}
```

## Change Preventers

Patterns that make changes difficult.

### Divergent Change

**Symptoms:**

- One class is changed for many different reasons
- Different types of changes affect different parts of the class
- Class has multiple axes of change

**Refactorings:**

- **Extract Class** - Split by reason for change

**Example:**

```typescript
// Smell: Class changed for different reasons
class Report {
  // Changed when business rules change
  calculateMetrics() { }

  // Changed when database schema changes
  fetchData() { }

  // Changed when output format changes
  formatAsHTML() { }
  formatAsPDF() { }
  formatAsCSV() { }
}

// Better: Single responsibility
class MetricsCalculator {
  calculate() { }
}

class ReportDataRepository {
  fetch() { }
}

class ReportFormatter {
  toHTML() { }
  toPDF() { }
  toCSV() { }
}
```

### Shotgun Surgery

**Symptoms:**

- Single change requires edits to many classes
- Related functionality is scattered
- Easy to miss a spot when making changes

**Refactorings:**

- **Move Method/Field** - Consolidate related code
- **Inline Class** - Merge overly distributed classes

**Example:**

```typescript
// Smell: Adding new field requires changes everywhere
// In User.ts
class User {
  name: string;
  email: string;
  // Add: phone: string;
}

// In UserRepository.ts
function saveUser(user: User) {
  db.query(`INSERT INTO users (name, email) ...`);
  // Must add: phone
}

// In UserValidator.ts
function validateUser(user: User) {
  validateEmail(user.email);
  // Must add: validatePhone(user.phone);
}

// In UserSerializer.ts
function serialize(user: User) {
  return { name: user.name, email: user.email };
  // Must add: phone
}

// Better: Encapsulate related logic
class User {
  name: string;
  email: string;
  phone: string;

  validate() {
    // All validation in one place
  }

  toDTO() {
    // All serialization in one place
  }
}
```

## Couplers

Code that creates excessive coupling between classes.

### Feature Envy

**Symptoms:**

- Method uses more features of another class than its own
- Method spends most of its time accessing another object's data
- Method would require fewer parameters if moved

**Refactorings:**

- **Move Method** - Put method with the data it uses
- **Extract Method** - Extract the envious portion, then move it

**Example:**

```typescript
// Smell: Method uses other class's data
class Order {
  customer: Customer;

  getDiscountedTotal(): number {
    // Uses lots of Customer data
    const loyaltyYears = this.customer.loyaltyYears;
    const totalPurchases = this.customer.totalPurchases;
    const membershipLevel = this.customer.membershipLevel;

    let discount = 0;
    if (loyaltyYears > 5) discount += 0.05;
    if (totalPurchases > 10000) discount += 0.05;
    if (membershipLevel === 'gold') discount += 0.1;

    return this.total * (1 - discount);
  }
}

// Better: Move calculation to Customer
class Customer {
  loyaltyYears: number;
  totalPurchases: number;
  membershipLevel: string;

  getDiscountRate(): number {
    let discount = 0;
    if (this.loyaltyYears > 5) discount += 0.05;
    if (this.totalPurchases > 10000) discount += 0.05;
    if (this.membershipLevel === 'gold') discount += 0.1;
    return discount;
  }
}

class Order {
  customer: Customer;

  getDiscountedTotal(): number {
    return this.total * (1 - this.customer.getDiscountRate());
  }
}
```

### Inappropriate Intimacy

**Symptoms:**

- Classes access each other's private fields/methods
- Bidirectional dependencies between classes
- Classes know too much about each other's implementation

**Refactorings:**

- **Move Method/Field** - Reduce sharing
- **Extract Class** - Create intermediary
- **Hide Delegate** - Add indirection
- **Change Bidirectional to Unidirectional**

### Message Chains

**Symptoms:**

- Long chains of method calls: `a.getB().getC().getD().doSomething()`
- Client depends on navigation structure
- Changes to intermediate structure break clients

**Refactorings:**

- **Hide Delegate** - Add wrapper methods
- **Extract Method** - Isolate chain usage
- **Move Method** - Put code closer to the data

**Example:**

```typescript
// Smell: Long navigation chain
function getManagerName(person: Person): string {
  return person
    .getDepartment()
    .getManager()
    .getName();
}

// Better: Hide delegation
class Person {
  getManagerName(): string {
    return this.department.getManagerName();
  }
}

class Department {
  getManagerName(): string {
    return this.manager.getName();
  }
}

// Client code
function getManagerName(person: Person): string {
  return person.getManagerName();
}
```

### Middle Man

**Symptoms:**

- Class delegates most of its work to another class
- Many methods just forward calls
- Class adds no value beyond delegation

**Refactorings:**

- **Remove Middle Man** - Have clients call delegate directly
- **Inline Method** - Remove pure delegation methods

**Example:**

```typescript
// Smell: Person delegates everything
class Person {
  department: Department;

  getManager() { return this.department.getManager(); }
  getDepartmentName() { return this.department.getName(); }
  getDepartmentBudget() { return this.department.getBudget(); }
  // ... 10 more delegation methods
}

// Better: Remove middle man
class Person {
  department: Department; // Let clients access directly when appropriate

  // Only keep methods that add value
  isInSameDepartment(other: Person): boolean {
    return this.department === other.department;
  }
}
```

## Dispensables

Code that serves no purpose.

### Dead Code

**Symptoms:**

- Unreachable code after return/throw
- Unused variables, parameters, or imports
- Methods never called
- Commented-out code

**Refactorings:**

- Delete it. Version control has the history.

### Speculative Generality

**Symptoms:**

- Abstract classes with only one subclass
- Parameters/methods for "future use"
- Complex design patterns for simple problems
- Comments explaining what this "will be used for"

**Refactorings:**

- **Collapse Hierarchy** - Remove unnecessary abstraction
- **Inline Class** - Remove unused classes
- **Remove Parameter** - Remove unused parameters

### Duplicate Code

**Symptoms:**

- Same code structure in multiple places
- Copy-pasted code with minor variations
- Similar algorithms with different data types

**Refactorings:**

- **Extract Method** - Pull common code into function
- **Extract Class** - For duplicate code across classes
- **Pull Up Method** - For duplicate code in siblings
- **Form Template Method** - For similar algorithms with variations

**Example:**

```typescript
// Smell: Duplicated validation
function validateUser(user: User) {
  if (!user.email || !user.email.includes('@')) {
    throw new Error('Invalid email');
  }
}

function validateOrder(order: Order) {
  if (!order.customerEmail || !order.customerEmail.includes('@')) {
    throw new Error('Invalid email');
  }
}

// Better: Extract common validation
function validateEmail(email: string): void {
  if (!email || !email.includes('@')) {
    throw new Error('Invalid email');
  }
}

function validateUser(user: User) {
  validateEmail(user.email);
}

function validateOrder(order: Order) {
  validateEmail(order.customerEmail);
}
```

## Quick Reference Table

| Smell                  | Key Indicator               | Primary Fix                |
|------------------------|-----------------------------|----------------------------|
| Long Method            | >20-30 lines                | Extract Function           |
| Large Class            | >15 methods, >10 fields     | Extract Class              |
| Long Parameter List    | >3-4 params                 | Introduce Parameter Object |
| Primitive Obsession    | Strings for domain concepts | Replace with Value Object  |
| Data Clumps            | Same fields grouped         | Extract Class              |
| Switch Statements      | Type-based conditionals     | Replace with Polymorphism  |
| Feature Envy           | Uses other class's data     | Move Method                |
| Message Chains         | a.b().c().d()               | Hide Delegate              |
| Duplicate Code         | Copy-paste                  | Extract Method             |
| Dead Code              | Unused code                 | Delete                     |
| Speculative Generality | "Future use"                | Inline/Collapse            |
