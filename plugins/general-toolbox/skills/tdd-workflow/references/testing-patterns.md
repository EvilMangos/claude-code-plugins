# Testing Patterns Reference

Common patterns and techniques for writing effective tests in TDD.

## Test Structure Patterns

### Arrange-Act-Assert (AAA)

Standard pattern for organizing test code:

```typescript
test('calculateDiscount applies percentage to total', () => {
  // Arrange - Set up test data and dependencies
  const cart = createCart([{ price: 100, quantity: 2 }]);
  const discount = { type: 'percentage', value: 10 };

  // Act - Execute the code under test
  const result = calculateDiscount(cart, discount);

  // Assert - Verify the outcome
  expect(result.discountAmount).toBe(20);
  expect(result.finalTotal).toBe(180);
});
```

### Given-When-Then (BDD Style)

Behavior-focused test organization:

```typescript
describe('User authentication', () => {
  describe('given valid credentials', () => {
    describe('when login is attempted', () => {
      it('then returns authentication token', async () => {
        const credentials = { email: 'user@test.com', password: 'valid' };
        const result = await authService.login(credentials);
        expect(result.token).toBeDefined();
      });
    });
  });
});
```

## Test Double Patterns

### Stub - Returns Predefined Values

Use when needing controlled return values:

```typescript
const userRepository = {
  findById: jest.fn().mockResolvedValue({ id: 1, name: 'Test User' })
};
```

### Mock - Verifies Interactions

Use when verifying method calls (sparingly):

```typescript
const emailService = { send: jest.fn() };
await resetPassword(emailService, 'user@test.com');
expect(emailService.send).toHaveBeenCalledWith(
  expect.objectContaining({ to: 'user@test.com' })
);
```

### Fake - Simplified Implementation

Use for complex dependencies:

```typescript
class FakeUserRepository {
  private users: User[] = [];

  async save(user: User) {
    this.users.push(user);
    return user;
  }

  async findById(id: string) {
    return this.users.find(u => u.id === id);
  }
}
```

## Edge Case Patterns

### Boundary Testing

Test at boundary values:

```typescript
describe('validateAge', () => {
  it('accepts minimum valid age (18)', () => {
    expect(validateAge(18)).toBe(true);
  });

  it('rejects one below minimum (17)', () => {
    expect(validateAge(17)).toBe(false);
  });

  it('accepts maximum valid age (120)', () => {
    expect(validateAge(120)).toBe(true);
  });

  it('rejects one above maximum (121)', () => {
    expect(validateAge(121)).toBe(false);
  });
});
```

### Empty/Null Testing

Test empty and null inputs:

```typescript
describe('processItems', () => {
  it('returns empty array for empty input', () => {
    expect(processItems([])).toEqual([]);
  });

  it('handles null input gracefully', () => {
    expect(processItems(null)).toEqual([]);
  });

  it('handles undefined input gracefully', () => {
    expect(processItems(undefined)).toEqual([]);
  });
});
```

## Error Testing Patterns

### Expected Exceptions

```typescript
it('throws ValidationError for invalid email', () => {
  expect(() => validateEmail('not-an-email')).toThrow(ValidationError);
});

it('throws with specific message', () => {
  expect(() => validateEmail('not-an-email'))
    .toThrow('Invalid email format');
});
```

### Async Error Testing

```typescript
it('rejects with NotFoundError when user missing', async () => {
  await expect(userService.getUser('nonexistent'))
    .rejects.toThrow(NotFoundError);
});
```

## Isolation Patterns

### Test Fixtures

Reusable test data setup:

```typescript
// fixtures/users.ts
export const validUser = {
  id: '1',
  email: 'test@example.com',
  name: 'Test User'
};

export const adminUser = {
  ...validUser,
  role: 'admin'
};

// In tests
import { validUser, adminUser } from './fixtures/users';
```

### Factory Functions

Generate test data with variations:

```typescript
function createUser(overrides: Partial<User> = {}): User {
  return {
    id: generateId(),
    email: 'default@test.com',
    name: 'Default Name',
    createdAt: new Date(),
    ...overrides
  };
}

// Usage
const user = createUser({ name: 'Custom Name' });
```

### Setup and Teardown

Proper test isolation:

```typescript
describe('Database operations', () => {
  let connection: Connection;

  beforeAll(async () => {
    connection = await createTestConnection();
  });

  afterAll(async () => {
    await connection.close();
  });

  beforeEach(async () => {
    await connection.clear(); // Clean slate for each test
  });

  it('saves user to database', async () => {
    // Test with clean database state
  });
});
```

## Async Testing Patterns

### Promise Resolution

```typescript
it('fetches user data', async () => {
  const user = await userService.fetch('123');
  expect(user.name).toBe('Expected Name');
});
```

### Timeout Handling

```typescript
it('times out slow operations', async () => {
  jest.useFakeTimers();

  const promise = slowOperation();
  jest.advanceTimersByTime(5000);

  await expect(promise).rejects.toThrow('Operation timed out');

  jest.useRealTimers();
});
```

## Anti-Patterns to Avoid

### Testing Implementation Details

```typescript
// BAD - Tests internal structure
it('calls private helper method', () => {
  const spy = jest.spyOn(service, '_privateHelper');
  service.publicMethod();
  expect(spy).toHaveBeenCalled();
});

// GOOD - Tests observable behavior
it('returns transformed data', () => {
  const result = service.publicMethod();
  expect(result).toEqual(expectedOutput);
});
```

### Over-Mocking

```typescript
// BAD - Mocks everything, tests nothing real
it('processes order', () => {
  const mockValidator = jest.fn().mockReturnValue(true);
  const mockCalculator = jest.fn().mockReturnValue(100);
  const mockSaver = jest.fn().mockResolvedValue({ id: 1 });
  // No real logic tested
});

// GOOD - Uses real logic, mocks only external boundaries
it('processes order', async () => {
  const fakeDb = new FakeOrderRepository();
  const service = new OrderService(fakeDb);

  const order = await service.process(validOrderData);

  expect(order.total).toBe(150); // Real calculation
  expect(order.status).toBe('confirmed'); // Real state transition
});
```

### Test Interdependence

```typescript
// BAD - Tests depend on order
let sharedUser: User;

it('creates user', async () => {
  sharedUser = await createUser();
});

it('updates user', async () => {
  await updateUser(sharedUser.id, { name: 'New' }); // Fails if first test fails
});

// GOOD - Independent tests
it('creates user', async () => {
  const user = await createUser();
  expect(user.id).toBeDefined();
});

it('updates user', async () => {
  const user = await createUser(); // Each test creates own data
  const updated = await updateUser(user.id, { name: 'New' });
  expect(updated.name).toBe('New');
});
```
