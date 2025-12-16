# What to Test: Coverage Decision Guide

Detailed guidance on making smart coverage decisions - what deserves tests and what doesn't.

## The Testing Value Equation

Before writing a test, consider:

```
Test Value = (Bug Risk × Impact) - (Writing Cost + Maintenance Cost)
```

High-value tests target code that:

- Has complex logic or many branches
- Handles money, security, or critical data
- Is frequently modified
- Has failed before

## What to Always Test

### Business Logic and Calculations

Any code that implements business rules or performs calculations:

```typescript
// ALWAYS TEST - Core business logic
function calculateOrderTotal(items: Item[], discount?: Discount): number {
  const subtotal = items.reduce((sum, item) => sum + item.price * item.quantity, 0);
  if (!discount) return subtotal;
  return discount.type === 'percentage'
    ? subtotal * (1 - discount.value / 100)
    : Math.max(0, subtotal - discount.value);
}

// Tests needed:
// - Empty items array
// - Single item, multiple items
// - With/without discount
// - Percentage vs fixed discount
// - Discount exceeding total
```

### Input Validation

All validation logic at system boundaries:

```typescript
// ALWAYS TEST - Validation
function validateEmail(email: string): boolean {
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return pattern.test(email);
}

// Tests needed:
// - Valid emails
// - Missing @ symbol
// - Missing domain
// - Empty string
// - Whitespace handling
```

### Error Handling

Code that handles failures:

```typescript
// ALWAYS TEST - Error handling
async function fetchUserSafe(id: string): Promise<User | null> {
  try {
    return await api.getUser(id);
  } catch (error) {
    if (error.status === 404) return null;
    throw new UserFetchError(error.message);
  }
}

// Tests needed:
// - Successful fetch
// - 404 returns null
// - Other errors throw UserFetchError
// - Error message preserved
```

### State Transitions

Code that manages state changes:

```typescript
// ALWAYS TEST - State machine
function transitionOrderStatus(current: Status, event: Event): Status {
  const transitions = {
    pending: { confirm: 'confirmed', cancel: 'cancelled' },
    confirmed: { ship: 'shipped', cancel: 'cancelled' },
    shipped: { deliver: 'delivered' }
  };
  const next = transitions[current]?.[event];
  if (!next) throw new InvalidTransitionError(current, event);
  return next;
}

// Tests needed:
// - Each valid transition
// - Invalid transitions throw
// - Terminal states (delivered, cancelled)
```

### Integration Points

Code that interacts with external systems:

```typescript
// ALWAYS TEST - External integration
async function syncUserToExternalCRM(user: User): Promise<SyncResult> {
  const payload = mapUserToCRMFormat(user);
  const response = await crmClient.upsert(payload);
  return { externalId: response.id, syncedAt: new Date() };
}

// Tests needed (with mocked CRM client):
// - Successful sync
// - Mapping correctness
// - API error handling
// - Retry behavior (if implemented)
```

## What to Skip Testing

### Simple Getters/Setters

No logic to verify:

```typescript
// SKIP - No logic
class User {
  private _name: string;

  get name() { return this._name; }
  set name(value: string) { this._name = value; }
}

// Don't test: get/set behavior is language-guaranteed
```

### Pass-Through Methods

Methods that just delegate without logic:

```typescript
// SKIP - Pure delegation
class UserService {
  constructor(private repository: UserRepository) {}

  findById(id: string) {
    return this.repository.findById(id);
  }
}

// Don't test: tests would just verify repository mock was called
// Test the repository directly instead
```

### Framework/Library Functionality

Don't test what you didn't write:

```typescript
// SKIP - Framework behavior
app.get('/users', (req, res) => {
  res.json(users);
});

// Don't test: Express routing works
// DO test: Your handler logic, response format
```

### Configuration Constants

Static values don't need tests:

```typescript
// SKIP - Constants
export const CONFIG = {
  MAX_RETRIES: 3,
  TIMEOUT_MS: 5000,
  API_VERSION: 'v2'
};

// Don't test: Values are obvious from code
```

### Trivial Transformations

One-liner mappings with no logic:

```typescript
// SKIP - Trivial mapping
const fullName = (user: User) => `${user.firstName} ${user.lastName}`;

// Consider skipping if:
// - No edge cases (null handling, etc.)
// - Used in tested code (covered indirectly)
```

## Edge Cases: The 80/20 Rule

Focus on edge cases most likely to cause bugs:

### High Priority Edge Cases

```typescript
// MUST TEST these edge cases
describe('divideNumbers', () => {
  it('handles division by zero', () => {
    expect(() => divide(10, 0)).toThrow('Division by zero');
  });
});

describe('processArray', () => {
  it('handles empty array', () => {
    expect(processArray([])).toEqual([]);
  });

  it('handles single element', () => {
    expect(processArray([1])).toEqual([1]);
  });
});

describe('parseDate', () => {
  it('handles invalid date string', () => {
    expect(parseDate('not-a-date')).toBeNull();
  });
});
```

### Lower Priority Edge Cases

```typescript
// MAY SKIP if unlikely in production
describe('processString', () => {
  // Skip if your app never handles these
  it('handles unicode emoji', () => { /* ... */ });
  it('handles right-to-left text', () => { /* ... */ });
  it('handles 10MB string', () => { /* ... */ });
});
```

## Mocking Decision Guide

### When to Mock

| Scenario         | Mock? | Reason                              |
|------------------|-------|-------------------------------------|
| Database calls   | Yes   | Slow, stateful, external            |
| HTTP APIs        | Yes   | Unreliable, slow, external          |
| File system      | Maybe | Mock for unit, real for integration |
| Time/Date        | Yes   | Non-deterministic                   |
| Internal classes | No    | Test real behavior                  |
| Pure functions   | No    | Deterministic, fast                 |

### Mock Boundaries, Not Internals

```typescript
// GOOD - Mock at the boundary
class OrderService {
  constructor(private db: Database, private paymentApi: PaymentAPI) {}

  async processOrder(order: Order) {
    const validated = this.validateOrder(order);  // Don't mock
    const enriched = this.enrichOrder(validated);  // Don't mock
    await this.db.save(enriched);                  // Mock this
    await this.paymentApi.charge(enriched.total);  // Mock this
    return enriched;
  }
}

// Test with:
const mockDb = { save: jest.fn() };
const mockPayment = { charge: jest.fn() };
// validateOrder and enrichOrder run as real code
```

## Coverage Metrics: Quality Over Quantity

### Meaningful Coverage

```typescript
// HIGH VALUE - Tests behavior
it('rejects expired tokens', () => {
  const expiredToken = createToken({ expiresAt: pastDate });
  expect(() => validateToken(expiredToken)).toThrow('Token expired');
});

// LOW VALUE - Just hits lines
it('calls all methods', () => {
  const service = new Service();
  service.methodA();  // Just for coverage
  service.methodB();  // Just for coverage
  // No assertions!
});
```

### Coverage Goals by Code Type

| Code Type         | Target Coverage | Notes                         |
|-------------------|-----------------|-------------------------------|
| Business logic    | 90-100%         | Critical paths fully covered  |
| Utilities/helpers | 80-90%          | Common cases + key edge cases |
| API handlers      | 70-80%          | Happy path + error handling   |
| Configuration     | 0-20%           | Only if complex logic         |
| Generated code    | 0%              | Don't test generated code     |

## Testing Existing Code

When adding tests to existing code, prioritize:

1. **Code that has caused bugs** - Prevent regressions
2. **Code being modified** - Test before changing
3. **High-risk code** - Security, payments, data integrity
4. **Complex code** - Many branches, nested conditions
5. **Frequently used code** - Utilities, shared functions

### Adding Tests Before Refactoring

```typescript
// Step 1: Characterization test (capture current behavior)
it('returns current behavior (characterization)', () => {
  // Document what code DOES, not what it SHOULD do
  expect(legacyFunction(input)).toMatchSnapshot();
});

// Step 2: Add specific behavior tests
it('handles empty input', () => {
  expect(legacyFunction([])).toEqual([]);
});

// Step 3: Refactor with confidence
// Tests catch regressions
```

## Summary Decision Tree

```
Should I write a test for this code?
│
├─ Does it contain business logic? → YES, test it
├─ Does it validate input? → YES, test it
├─ Does it handle errors? → YES, test it
├─ Has it caused bugs before? → YES, test it
├─ Is it frequently modified? → YES, test it
│
├─ Is it a simple getter/setter? → NO, skip
├─ Is it a pass-through method? → NO, skip
├─ Is it framework code? → NO, skip
├─ Is it a constant? → NO, skip
│
└─ Still unsure?
   ├─ Would a bug here be caught elsewhere? → Maybe skip
   ├─ Would a bug here cause user impact? → Test it
   └─ Is the test easy to write and maintain? → Test it
```
