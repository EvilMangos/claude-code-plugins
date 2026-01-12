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

### Configuration and Environment Loading

Never write tests that simply verify environment variables are loaded into config objects, or that framework features like immutability work correctly:

```python
# SKIP - Simple environment variable loading
def test_loads_api_key_from_environment():
    """Don't test: reading env var and storing in config field is pass-through."""
    os.environ['API_KEY'] = 'test_key'
    config = load_config()
    assert config.api_key == 'test_key'  # No logic to verify

# SKIP - Default value application
def test_uses_default_timeout_when_not_provided():
    """Don't test: simple default value logic is trivial."""
    config = load_config()
    assert config.timeout == 30  # Just checking a default constant

# SKIP - Testing framework features
def test_config_is_immutable():
    """Don't test: @dataclass(frozen=True) immutability is Python's responsibility."""
    config = Config(api_key='key')
    with pytest.raises(AttributeError):
        config.api_key = 'new_key'  # Testing Python, not your code

def test_config_stores_all_fields():
    """Don't test: field storage is guaranteed by the language/framework."""
    config = Config(api_key='key', timeout=60)
    assert config.api_key == 'key'  # Testing basic object construction
    assert config.timeout == 60
```

```typescript
// SKIP - Environment loading without logic
describe('Config', () => {
  it('loads PORT from environment', () => {
    process.env.PORT = '3000';
    const config = loadConfig();
    expect(config.port).toBe(3000);  // No logic, just pass-through
  });

  it('uses default port when not set', () => {
    const config = loadConfig();
    expect(config.port).toBe(8080);  // Testing a simple default
  });
});

// SKIP - Testing DTO/class features
it('config object is readonly', () => {
  const config = new Config({ apiKey: 'key' });
  expect(() => config.apiKey = 'new').toThrow();  // Testing readonly modifier
});
```

**Why skip configuration loading tests:**

- Loading env vars into fields is pass-through logic with no behavior to verify
- Default values are static constants, obvious from code
- Framework features (immutability, readonly, field storage) are language-guaranteed
- These tests break on every refactor without catching real bugs
- High maintenance cost, zero bug prevention value

**What to DO test for configuration:**

- **Validation logic** - missing required fields, invalid formats (see "Input Validation" section)
- **Complex transformations** - parsing, normalization, computed values with business logic
- **Configuration-driven behavior** - how your code behaves differently based on config values

```python
# DO TEST - Validation at system boundary
def test_raises_error_when_required_api_key_missing():
    """DO test: validation is real logic that prevents invalid states."""
    with pytest.raises(ConfigurationError, match="API_KEY is required"):
        load_config()  # Missing required env var

def test_raises_error_when_port_not_numeric():
    """DO test: format validation catches configuration mistakes."""
    os.environ['PORT'] = 'not_a_number'
    with pytest.raises(ConfigurationError, match="PORT must be numeric"):
        load_config()
```

### Interfaces and Abstractions

Never write tests for interfaces, abstract classes, protocols, or pure contracts:

```typescript
// SKIP - This is an interface, not testable behavior
interface IUserRepository {
  findById(id: string): Promise<User | null>;
  save(user: User): Promise<void>;
}

// SKIP - Abstract class defines contract, not behavior
abstract class BaseValidator {
  abstract validate(input: unknown): ValidationResult;
}

// DO TEST - Concrete implementations that fulfill the contract
class PostgresUserRepository implements IUserRepository {
  async findById(id: string): Promise<User | null> {
    // Real implementation with real behavior to test
  }
  async save(user: User): Promise<void> {
    // Real implementation with real behavior to test
  }
}
```

**Why skip abstraction testing:**

- Interfaces have no behavior to verify – they define contracts, not implementations
- Abstract classes without concrete methods have nothing to execute
- Tests verify that *implementations* fulfill contracts correctly
- Testing abstractions leads to empty tests that provide false confidence

**What to do instead:**

- Write tests for each concrete implementation
- Use interface-based tests to verify implementations fulfill the contract
- Test behavior, not type signatures

### Module Exports and Re-exports

Never write tests that verify what a module exports:

```typescript
// SKIP - Testing module structure, not behavior
describe('index.ts exports', () => {
  it('exports UserService', () => {
    expect(index.UserService).toBeDefined();
  });

  it('re-exports types from user.types', () => {
    expect(index.UserDTO).toBeDefined();
  });
});

// SKIP - Testing barrel file completeness
describe('public API', () => {
  it('exports all models', () => {
    expect(Object.keys(models)).toContain('User');
    expect(Object.keys(models)).toContain('Order');
  });
});
```

**Why skip export testing:**

- Exports are static module structure, not runtime behavior
- TypeScript/linting catches missing exports at compile time
- These tests break on any refactor without catching real bugs
- If an export is used, a real test will import and use it anyway

**What to do instead:**

- Trust the compiler to catch export errors
- Write tests that use the exported functionality (which implicitly verifies the export works)
- Use integration tests that exercise the public API

### Private and Protected Methods

Never write tests that directly call private or protected methods:

```typescript
// SKIP - Testing private methods directly
class OrderProcessor {
  private calculateTax(amount: number): number {
    return amount * 0.1;
  }

  protected validateOrder(order: Order): boolean {
    return order.items.length > 0 && order.total > 0;
  }

  public processOrder(order: Order): ProcessedOrder {
    if (!this.validateOrder(order)) throw new Error('Invalid order');
    const tax = this.calculateTax(order.total);
    return { ...order, tax, grandTotal: order.total + tax };
  }
}

// DON'T DO THIS - Accessing private methods for testing
describe('OrderProcessor internals', () => {
  it('calculates tax correctly', () => {
    const processor = new OrderProcessor();
    // Bypassing access modifiers to test internals
    expect((processor as any).calculateTax(100)).toBe(10);
  });

  it('validates order structure', () => {
    const processor = new OrderProcessor();
    // Testing protected method directly
    expect((processor as any).validateOrder(invalidOrder)).toBe(false);
  });
});

// DO THIS - Test through the public interface
describe('OrderProcessor', () => {
  it('includes correct tax in processed order', () => {
    const processor = new OrderProcessor();
    const result = processor.processOrder({ items: [item], total: 100 });
    expect(result.tax).toBe(10);
    expect(result.grandTotal).toBe(110);
  });

  it('rejects invalid orders', () => {
    const processor = new OrderProcessor();
    expect(() => processor.processOrder({ items: [], total: 0 }))
      .toThrow('Invalid order');
  });
});
```

```python
# SKIP - Testing private/protected methods in Python
class PaymentService:
    def _validate_card(self, card_number: str) -> bool:
        """Private method - single underscore convention."""
        return len(card_number) == 16 and card_number.isdigit()

    def __calculate_fee(self, amount: float) -> float:
        """Name-mangled method - double underscore."""
        return amount * 0.029

    def process_payment(self, card_number: str, amount: float) -> dict:
        if not self._validate_card(card_number):
            raise ValueError("Invalid card number")
        fee = self.__calculate_fee(amount)
        return {"amount": amount, "fee": fee, "total": amount + fee}

# DON'T DO THIS
def test_validate_card_directly():
    service = PaymentService()
    assert service._validate_card("1234567890123456") == True  # Accessing private

def test_calculate_fee_directly():
    service = PaymentService()
    # Accessing name-mangled method
    assert service._PaymentService__calculate_fee(100) == 2.9

# DO THIS - Test through public interface
def test_rejects_invalid_card_numbers():
    service = PaymentService()
    with pytest.raises(ValueError, match="Invalid card number"):
        service.process_payment("invalid", 100.0)

def test_includes_correct_fee_in_payment():
    service = PaymentService()
    result = service.process_payment("1234567890123456", 100.0)
    assert result["fee"] == 2.9
    assert result["total"] == 102.9
```

**Why skip private/protected method testing:**

- **Encapsulation violation** - Private methods are implementation details; testing them couples tests to internal structure
- **Refactoring friction** - Tests break when you reorganize internals, even if behavior is unchanged
- **False confidence** - Private method tests can pass while public behavior is broken
- **Code smell indicator** - Needing to test a private method often signals it should be extracted to a separate, testable class
- **Language intent** - Access modifiers exist to define API boundaries; tests should respect them

**What to do instead:**

- Test private behavior through public methods that use it
- If a private method is complex enough to need its own tests, extract it to a separate class/module with a public interface
- Use characterization tests on public methods to ensure private logic works correctly
- Consider if the private method's complexity indicates a missing abstraction

**When private methods seem "too complex" to test indirectly:**

```typescript
// If you feel you NEED to test this private method...
class ReportGenerator {
  private parseComplexFormat(data: string): ParsedData {
    // 50 lines of complex parsing logic
  }

  public generateReport(rawData: string): Report {
    const parsed = this.parseComplexFormat(rawData);
    return this.formatReport(parsed);
  }
}

// ...it's a sign to extract it
class ComplexFormatParser {
  public parse(data: string): ParsedData {
    // Same logic, now testable through public interface
  }
}

class ReportGenerator {
  constructor(private parser: ComplexFormatParser) {}

  public generateReport(rawData: string): Report {
    const parsed = this.parser.parse(rawData);
    return this.formatReport(parsed);
  }
}

// Now you can test the parser directly
describe('ComplexFormatParser', () => {
  it('parses valid format correctly', () => {
    const parser = new ComplexFormatParser();
    expect(parser.parse(validInput)).toEqual(expectedOutput);
  });
});
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
├─ Is it simple config/env loading? → NO, skip
├─ Is it framework code? → NO, skip
├─ Is it a constant? → NO, skip
├─ Is it a private/protected method? → NO, test via public interface
│
└─ Still unsure?
   ├─ Would a bug here be caught elsewhere? → Maybe skip
   ├─ Would a bug here cause user impact? → Test it
   └─ Is the test easy to write and maintain? → Test it
```
