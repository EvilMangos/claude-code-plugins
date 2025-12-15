# Refactoring Patterns Catalog

Comprehensive catalog of refactoring patterns with detailed explanations, mechanics, and examples.

## Composing Methods

### Extract Function

**Motivation:** Turn a code fragment into a function with a name that explains its purpose.

**Mechanics:**
1. Create a new function named after what it does (not how)
2. Copy the extracted code into the new function
3. Scan for local variables - pass as parameters or extract as needed
4. Replace original code with function call
5. Test

**Example - TypeScript:**
```typescript
// Before
function printOwing(invoice: Invoice) {
  let outstanding = 0;

  console.log("***********************");
  console.log("**** Customer Owes ****");
  console.log("***********************");

  for (const o of invoice.orders) {
    outstanding += o.amount;
  }

  console.log(`name: ${invoice.customer}`);
  console.log(`amount: ${outstanding}`);
}

// After
function printOwing(invoice: Invoice) {
  printBanner();
  const outstanding = calculateOutstanding(invoice);
  printDetails(invoice, outstanding);
}

function printBanner() {
  console.log("***********************");
  console.log("**** Customer Owes ****");
  console.log("***********************");
}

function calculateOutstanding(invoice: Invoice): number {
  return invoice.orders.reduce((sum, o) => sum + o.amount, 0);
}

function printDetails(invoice: Invoice, outstanding: number) {
  console.log(`name: ${invoice.customer}`);
  console.log(`amount: ${outstanding}`);
}
```

**Example - Python:**
```python
# Before
def print_owing(invoice):
    outstanding = 0

    print("***********************")
    print("**** Customer Owes ****")
    print("***********************")

    for o in invoice.orders:
        outstanding += o.amount

    print(f"name: {invoice.customer}")
    print(f"amount: {outstanding}")

# After
def print_owing(invoice):
    print_banner()
    outstanding = calculate_outstanding(invoice)
    print_details(invoice, outstanding)

def print_banner():
    print("***********************")
    print("**** Customer Owes ****")
    print("***********************")

def calculate_outstanding(invoice):
    return sum(o.amount for o in invoice.orders)

def print_details(invoice, outstanding):
    print(f"name: {invoice.customer}")
    print(f"amount: {outstanding}")
```

### Inline Function

**Motivation:** Remove unnecessary indirection when function body is as clear as its name.

**Mechanics:**
1. Check function is not polymorphic (not overridden in subclasses)
2. Find all call sites
3. Replace each call with function body
4. Test after each replacement
5. Remove function definition

**Example:**
```typescript
// Before
function getRating(driver: Driver): number {
  return moreThanFiveLateDeliveries(driver) ? 2 : 1;
}

function moreThanFiveLateDeliveries(driver: Driver): boolean {
  return driver.numberOfLateDeliveries > 5;
}

// After
function getRating(driver: Driver): number {
  return driver.numberOfLateDeliveries > 5 ? 2 : 1;
}
```

### Extract Variable

**Motivation:** Break down complex expressions into named parts for clarity.

**Mechanics:**
1. Ensure expression has no side effects
2. Declare immutable variable, set to expression result
3. Replace original expression with variable reference
4. Test

**Example:**
```typescript
// Before
function price(order: Order): number {
  return order.quantity * order.itemPrice -
    Math.max(0, order.quantity - 500) * order.itemPrice * 0.05 +
    Math.min(order.quantity * order.itemPrice * 0.1, 100);
}

// After
function price(order: Order): number {
  const basePrice = order.quantity * order.itemPrice;
  const quantityDiscount = Math.max(0, order.quantity - 500) * order.itemPrice * 0.05;
  const shipping = Math.min(basePrice * 0.1, 100);
  return basePrice - quantityDiscount + shipping;
}
```

### Inline Variable

**Motivation:** Remove variable when it adds no clarity over the expression.

**Example:**
```typescript
// Before
const basePrice = order.basePrice;
return basePrice > 1000;

// After
return order.basePrice > 1000;
```

## Moving Features

### Move Function

**Motivation:** Place function with the data it uses most, or with functions it calls most.

**Mechanics:**
1. Examine what current context the function uses
2. Consider if function should move with related functions
3. Check for polymorphism in source class
4. Copy function to target context
5. Adjust for new context (parameters, references)
6. Reference new function from source (delegate)
7. Test
8. Remove source function or keep as delegating wrapper
9. Test

**Example:**
```typescript
// Before - function in Account class uses too much from AccountType
class Account {
  type: AccountType;
  daysOverdrawn: number;

  get bankCharge(): number {
    let result = 4.5;
    if (this.daysOverdrawn > 0) {
      result += this.type.overdraftCharge(this.daysOverdrawn);
    }
    return result;
  }
}

class AccountType {
  isPremium: boolean;

  overdraftCharge(daysOverdrawn: number): number {
    if (this.isPremium) {
      const baseCharge = 10;
      if (daysOverdrawn <= 7) return baseCharge;
      return baseCharge + (daysOverdrawn - 7) * 0.85;
    }
    return daysOverdrawn * 1.75;
  }
}

// After - bankCharge calculation moved to AccountType
class Account {
  type: AccountType;
  daysOverdrawn: number;

  get bankCharge(): number {
    return this.type.bankCharge(this);
  }
}

class AccountType {
  isPremium: boolean;

  bankCharge(account: Account): number {
    let result = 4.5;
    if (account.daysOverdrawn > 0) {
      result += this.overdraftCharge(account.daysOverdrawn);
    }
    return result;
  }

  overdraftCharge(daysOverdrawn: number): number {
    // ... same as before
  }
}
```

### Move Field

**Motivation:** Move data closer to the code that uses it most.

**Mechanics:**
1. Ensure field is encapsulated (getter/setter)
2. Create field and accessors in target
3. Redirect source accessors to target
4. Test
5. Remove source field

### Move Statements into Function

**Motivation:** Consolidate repeated code that always accompanies a function call.

**Example:**
```typescript
// Before
result.push(`<p>title: ${person.photo.title}</p>`);
result.concat(photoData(person.photo));

function photoData(photo: Photo): string[] {
  return [
    `<p>location: ${photo.location}</p>`,
    `<p>date: ${photo.date.toDateString()}</p>`,
  ];
}

// After
result.concat(photoData(person.photo));

function photoData(photo: Photo): string[] {
  return [
    `<p>title: ${photo.title}</p>`,
    `<p>location: ${photo.location}</p>`,
    `<p>date: ${photo.date.toDateString()}</p>`,
  ];
}
```

### Move Statements to Callers

**Motivation:** When function does too much and callers need different behavior.

**Mechanics:**
1. Extract statements to move into new function
2. Inline extracted function into all callers
3. Remove extracted function

## Organizing Data

### Split Variable

**Motivation:** Separate variables that are assigned more than once for different purposes.

**Example:**
```typescript
// Before
let temp = 2 * (height + width);
console.log(temp);
temp = height * width;
console.log(temp);

// After
const perimeter = 2 * (height + width);
console.log(perimeter);
const area = height * width;
console.log(area);
```

### Replace Derived Variable with Query

**Motivation:** Remove mutable state by calculating values on demand.

**Example:**
```typescript
// Before
class ProductionPlan {
  private _production: number = 0;
  private _adjustments: Adjustment[] = [];

  get production() { return this._production; }

  applyAdjustment(adjustment: Adjustment) {
    this._adjustments.push(adjustment);
    this._production += adjustment.amount;
  }
}

// After
class ProductionPlan {
  private _adjustments: Adjustment[] = [];

  get production() {
    return this._adjustments.reduce((sum, a) => sum + a.amount, 0);
  }

  applyAdjustment(adjustment: Adjustment) {
    this._adjustments.push(adjustment);
  }
}
```

### Replace Magic Literal

**Motivation:** Give meaning to literal values.

**Example:**
```typescript
// Before
function potentialEnergy(mass: number, height: number): number {
  return mass * 9.81 * height;
}

// After
const STANDARD_GRAVITY = 9.81;

function potentialEnergy(mass: number, height: number): number {
  return mass * STANDARD_GRAVITY * height;
}
```

## Simplifying Conditional Logic

### Decompose Conditional

**Motivation:** Extract condition and branches into clearly named functions.

**Example:**
```typescript
// Before
if (date < SUMMER_START || date > SUMMER_END) {
  charge = quantity * winterRate + winterServiceCharge;
} else {
  charge = quantity * summerRate;
}

// After
if (isSummer(date)) {
  charge = summerCharge(quantity);
} else {
  charge = winterCharge(quantity);
}

function isSummer(date: Date): boolean {
  return date >= SUMMER_START && date <= SUMMER_END;
}

function summerCharge(quantity: number): number {
  return quantity * summerRate;
}

function winterCharge(quantity: number): number {
  return quantity * winterRate + winterServiceCharge;
}
```

### Consolidate Conditional Expression

**Motivation:** Combine conditionals with same outcome into single check.

**Example:**
```typescript
// Before
function disabilityAmount(employee: Employee): number {
  if (employee.seniority < 2) return 0;
  if (employee.monthsDisabled > 12) return 0;
  if (employee.isPartTime) return 0;
  // compute disability amount
}

// After
function disabilityAmount(employee: Employee): number {
  if (isNotEligibleForDisability(employee)) return 0;
  // compute disability amount
}

function isNotEligibleForDisability(employee: Employee): boolean {
  return employee.seniority < 2
    || employee.monthsDisabled > 12
    || employee.isPartTime;
}
```

### Replace Nested Conditional with Guard Clauses

**Motivation:** Use early returns to reduce nesting and highlight special cases.

**Example:**
```typescript
// Before
function payAmount(employee: Employee): Money {
  let result: Money;
  if (employee.isSeparated) {
    result = { amount: 0, currency: 'USD' };
  } else {
    if (employee.isRetired) {
      result = retiredAmount();
    } else {
      result = normalPayAmount();
    }
  }
  return result;
}

// After
function payAmount(employee: Employee): Money {
  if (employee.isSeparated) return { amount: 0, currency: 'USD' };
  if (employee.isRetired) return retiredAmount();
  return normalPayAmount();
}
```

### Replace Conditional with Polymorphism

**Motivation:** Replace type-based conditionals with polymorphic dispatch.

**Mechanics:**
1. Create class hierarchy if none exists
2. Use factory to return appropriate subclass
3. Move conditional logic to superclass as default
4. Create subclass methods that override specific cases
5. Remove conditional from superclass

**Example:**
```typescript
// Before
function plumage(bird: Bird): string {
  switch (bird.type) {
    case 'EuropeanSwallow':
      return 'average';
    case 'AfricanSwallow':
      return bird.numberOfCoconuts > 2 ? 'tired' : 'average';
    case 'NorwegianBlueParrot':
      return bird.voltage > 100 ? 'scorched' : 'beautiful';
    default:
      return 'unknown';
  }
}

// After
abstract class Bird {
  abstract get plumage(): string;
}

class EuropeanSwallow extends Bird {
  get plumage() { return 'average'; }
}

class AfricanSwallow extends Bird {
  numberOfCoconuts: number;
  get plumage() { return this.numberOfCoconuts > 2 ? 'tired' : 'average'; }
}

class NorwegianBlueParrot extends Bird {
  voltage: number;
  get plumage() { return this.voltage > 100 ? 'scorched' : 'beautiful'; }
}

function createBird(data: BirdData): Bird {
  switch (data.type) {
    case 'EuropeanSwallow': return new EuropeanSwallow();
    case 'AfricanSwallow': return new AfricanSwallow(data.numberOfCoconuts);
    case 'NorwegianBlueParrot': return new NorwegianBlueParrot(data.voltage);
    default: throw new Error(`Unknown bird type: ${data.type}`);
  }
}
```

### Introduce Special Case (Null Object)

**Motivation:** Replace null checks with polymorphic behavior.

**Example:**
```typescript
// Before
if (customer === null) {
  customerName = 'occupant';
} else {
  customerName = customer.name;
}

// After
class Customer {
  get name() { return this._name; }
}

class UnknownCustomer extends Customer {
  get name() { return 'occupant'; }
}

// Usage
customerName = customer.name; // Works for both Customer and UnknownCustomer
```

## Refactoring APIs

### Separate Query from Modifier

**Motivation:** Functions should either return a value OR change state, not both.

**Example:**
```typescript
// Before
function alertForMiscreant(people: string[]): string {
  for (const p of people) {
    if (p === 'Don') {
      setOffAlarms();
      return 'Don';
    }
    if (p === 'John') {
      setOffAlarms();
      return 'John';
    }
  }
  return '';
}

// After
function findMiscreant(people: string[]): string {
  for (const p of people) {
    if (p === 'Don' || p === 'John') return p;
  }
  return '';
}

function alertForMiscreant(people: string[]): void {
  if (findMiscreant(people) !== '') setOffAlarms();
}
```

### Parameterize Function

**Motivation:** Combine similar functions that differ only by literal values.

**Example:**
```typescript
// Before
function tenPercentRaise(person: Person) {
  person.salary = person.salary.multiply(1.1);
}

function fivePercentRaise(person: Person) {
  person.salary = person.salary.multiply(1.05);
}

// After
function raise(person: Person, factor: number) {
  person.salary = person.salary.multiply(1 + factor);
}
```

### Replace Parameter with Query

**Motivation:** Remove parameter when receiver can calculate it.

**Example:**
```typescript
// Before
class Order {
  get finalPrice(): number {
    const basePrice = this.quantity * this.itemPrice;
    return this.discountedPrice(basePrice, this.discountLevel);
  }

  discountedPrice(basePrice: number, discountLevel: number): number {
    switch (discountLevel) {
      case 1: return basePrice * 0.95;
      case 2: return basePrice * 0.90;
      default: return basePrice;
    }
  }
}

// After
class Order {
  get finalPrice(): number {
    const basePrice = this.quantity * this.itemPrice;
    return this.discountedPrice(basePrice);
  }

  get discountLevel(): number {
    return this.quantity > 100 ? 2 : 1;
  }

  discountedPrice(basePrice: number): number {
    switch (this.discountLevel) {
      case 1: return basePrice * 0.95;
      case 2: return basePrice * 0.90;
      default: return basePrice;
    }
  }
}
```

### Remove Flag Argument

**Motivation:** Replace boolean flags with explicit functions.

**Example:**
```typescript
// Before
function setDimension(name: string, value: number, isMetric: boolean) {
  if (isMetric) {
    this.dimensions[name] = value;
  } else {
    this.dimensions[name] = value * 0.0254; // Convert inches to meters
  }
}

// After
function setDimensionInMeters(name: string, value: number) {
  this.dimensions[name] = value;
}

function setDimensionInInches(name: string, value: number) {
  this.dimensions[name] = value * 0.0254;
}
```

## Dealing with Inheritance

### Pull Up Method

**Motivation:** Remove duplicate code in subclasses by moving to superclass.

### Push Down Method

**Motivation:** Method only relevant to one subclass.

### Replace Superclass with Delegate

**Motivation:** Inheritance relationship is inappropriate (violates LSP).

**Example:**
```typescript
// Before - Stack inherits from List but shouldn't expose all List methods
class Stack<T> extends List<T> {
  push(item: T) { this.add(item); }
  pop(): T { return this.remove(this.size() - 1); }
}

// After - Stack delegates to List
class Stack<T> {
  private storage = new List<T>();

  push(item: T) { this.storage.add(item); }
  pop(): T { return this.storage.remove(this.storage.size() - 1); }
}
```

### Replace Subclass with Delegate

**Motivation:** Single inheritance is limiting or subclass variations are transient.

This pattern replaces a class hierarchy with composition, using delegates to vary behavior.

## Encapsulation

### Encapsulate Record

**Motivation:** Make data structures mutable only through controlled interface.

**Example:**
```typescript
// Before
const organization = { name: 'Acme', country: 'US' };

// After
class Organization {
  private _name: string;
  private _country: string;

  constructor(data: { name: string; country: string }) {
    this._name = data.name;
    this._country = data.country;
  }

  get name() { return this._name; }
  set name(value: string) { this._name = value; }
  get country() { return this._country; }
  set country(value: string) { this._country = value; }
}
```

### Encapsulate Collection

**Motivation:** Prevent uncontrolled modification of collections.

**Example:**
```typescript
// Before
class Person {
  courses: Course[] = [];
}

// Can add courses directly, bypassing any invariants
person.courses.push(newCourse);

// After
class Person {
  private _courses: Course[] = [];

  get courses(): readonly Course[] {
    return this._courses;
  }

  addCourse(course: Course) {
    this._courses.push(course);
  }

  removeCourse(course: Course) {
    const index = this._courses.indexOf(course);
    if (index > -1) this._courses.splice(index, 1);
  }
}
```

### Hide Delegate

**Motivation:** Reduce coupling by hiding implementation objects.

**Example:**
```typescript
// Before - Client knows about Department
manager = person.department.manager;

// After - Person hides Department
class Person {
  get manager() { return this.department.manager; }
}

// Client code
manager = person.manager;
```
