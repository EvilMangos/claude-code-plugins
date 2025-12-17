---
name: test-best-practices
description: This skill should be used when the user asks to "write tests", "add tests", "improve tests", "refactor tests", "review test quality", "fix flaky tests", "mock dependencies", "test this function", "what should I test", "how should I structure my tests", "what's the best way to mock this dependency", "how do I organize test fixtures", "what should I name this test", "how do I test async code", "how much test coverage do I need", "my tests are brittle", or needs guidance on testing patterns (AAA, test doubles), test isolation, mocking strategies, fixture organization, test naming, async testing, and coverage decisions.
---

# Test Best Practices Guide

Guidance for writing effective, maintainable tests that verify behavior without coupling to implementation details.

## Core Principles

### Test Observable Behavior, Not Implementation

Focus tests on what the code does, not how it does it:

**Verify:**

- Return values and outputs
- State changes (database, files, external systems)
- Emitted events or messages
- Error conditions and exceptions

**Avoid testing:**

- Private methods or internal helpers
- Exact implementation details (call order, internal state)
- Framework internals or library behavior

### What to Test vs What to Skip

**Always test:**

- Business logic and calculations
- Input validation and error handling
- Edge cases and boundary conditions
- Integration points with external systems
- State transitions and workflows

**Skip testing:**

- Simple getters/setters with no logic
- Framework-provided functionality
- Third-party library internals
- Trivial one-liner pass-through methods
- Configuration constants

### Coverage Requirements

Cover every behavioral requirement:

- **Normal paths** - expected inputs produce expected outputs
- **Edge cases** - boundary values, empty collections, nulls
- **Error paths** - invalid inputs, failure conditions, timeouts

**Coverage Targets:**

| Code Type              | Target   | Rationale                                |
|------------------------|----------|------------------------------------------|
| Business logic/core    | 80-90%   | Critical paths need thorough coverage    |
| API endpoints          | 70-80%   | Integration tests cover main flows       |
| Utilities/helpers      | 60-70%   | Test complex logic, skip trivial wrappers|
| Generated/boilerplate  | 0%       | No value in testing scaffolding          |

**Coverage Metrics That Matter:**

- **Branch coverage** over line coverage - ensures conditionals are tested
- **Critical path coverage** - prioritize business-critical flows
- **Mutation testing** - validates test quality, not just quantity

**Coverage Pitfalls:**

- High coverage ≠ good tests (can have 100% coverage with meaningless assertions)
- Don't chase coverage numbers - focus on behavior verification
- Exclude generated code, migrations, and config from metrics

## Test Structure

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

### Test Naming

Use descriptive names that explain the scenario and expected outcome:

```
test_<function>_<scenario>_<expected_result>

Examples:
test_login_with_valid_credentials_returns_token
test_login_with_invalid_password_raises_auth_error
test_calculate_total_with_empty_cart_returns_zero
```

## Mocking Strategy

### When to Mock

**Mock external boundaries:**

- Database connections
- HTTP/API calls
- File system operations
- Time-dependent operations
- Third-party services

**Avoid mocking:**

- Internal classes and helpers
- Simple data transformations
- Code under test itself

### Mock Types

| Type     | Purpose                   | Use Case                            |
|----------|---------------------------|-------------------------------------|
| **Stub** | Return predefined values  | Need controlled return values       |
| **Mock** | Verify interactions       | Verify method was called correctly  |
| **Fake** | Simplified implementation | Complex dependencies (in-memory DB) |

### Over-Mocking Anti-Pattern

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

## Test Independence

Ensure tests can run in any order:

- Set up required state within each test
- Clean up after tests (DB, files, env vars)
- Never share mutable state between tests
- Use controlled time/randomness for determinism

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
it('updates user', async () => {
  const user = await createUser(); // Each test creates own data
  const updated = await updateUser(user.id, { name: 'New' });
  expect(updated.name).toBe('New');
});
```

## Async Testing Patterns

### Handling Promises

Always await async operations and use proper assertion patterns:

```typescript
// TypeScript/Jest
it('fetches user data', async () => {
  const user = await userService.getById(1);
  expect(user.name).toBe('Alice');
});

// Test rejected promises
it('throws on invalid id', async () => {
  await expect(userService.getById(-1)).rejects.toThrow('Invalid ID');
});
```

```python
# Python/pytest
@pytest.mark.asyncio
async def test_fetches_user_data():
    user = await user_service.get_by_id(1)
    assert user.name == "Alice"

# Test exceptions
@pytest.mark.asyncio
async def test_throws_on_invalid_id():
    with pytest.raises(ValueError, match="Invalid ID"):
        await user_service.get_by_id(-1)
```

### Testing Timeouts and Delays

Control time-dependent behavior without actual waits:

```typescript
// Jest - use fake timers
jest.useFakeTimers();

it('retries after delay', async () => {
  const promise = service.fetchWithRetry();

  jest.advanceTimersByTime(1000); // Skip 1 second
  await promise;

  expect(fetchMock).toHaveBeenCalledTimes(2);
});
```

### Testing Concurrent Operations

Verify behavior when multiple async operations run together:

```typescript
it('handles concurrent updates', async () => {
  const updates = [
    service.update(1, { count: 10 }),
    service.update(1, { count: 20 }),
  ];

  await Promise.all(updates);

  const result = await service.get(1);
  expect([10, 20]).toContain(result.count); // Either value is valid
});
```

### Async Anti-Patterns

| Anti-Pattern             | Problem                          | Solution                     |
|--------------------------|----------------------------------|------------------------------|
| Missing `await`          | Test passes before async completes| Always await async operations|
| Real timers in tests     | Slow, flaky tests                | Use fake timers              |
| Unhandled rejections     | Silent failures                  | Assert on rejections explicitly|
| Race condition ignorance | Intermittent failures            | Test concurrent scenarios    |

## Common Anti-Patterns

| Anti-Pattern           | Problem                                   | Solution                       |
|------------------------|-------------------------------------------|--------------------------------|
| Testing implementation | Breaks when refactoring                   | Test observable outcomes       |
| Over-mocking           | Tests pass but don't verify real behavior | Mock only external boundaries  |
| Test interdependence   | Cascading failures, order-dependent       | Each test sets up own state    |
| Asserting too much     | Unclear what's being tested               | One logical assertion per test |
| Testing trivial code   | Wasted effort, maintenance burden         | Focus on business logic        |
| Ignoring edge cases    | Bugs in boundary conditions               | Test boundaries explicitly     |

## Additional Resources

### Reference Files

For detailed patterns and techniques, consult:

- **`references/testing-patterns.md`** - Test doubles, fixtures, factories, async testing patterns
- **`references/what-to-test.md`** - Detailed guidance on coverage decisions and edge cases

### Examples

Working examples in `examples/`:

- **`examples/adding-tests-to-existing-code.md`** - Step-by-step guide for testing existing functionality

### Related Skills

For TDD workflow (RED-GREEN-REFACTOR cycle), see the `tdd-workflow` skill.
