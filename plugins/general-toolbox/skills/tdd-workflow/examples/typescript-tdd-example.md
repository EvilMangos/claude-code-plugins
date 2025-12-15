# TDD Walkthrough: Building a Shopping Cart

A step-by-step demonstration of TDD building a shopping cart total calculator.

## Requirement

Build a function that calculates the total price of items in a shopping cart, supporting quantity and discounts.

## Cycle 1: Basic Total Calculation

### RED: Write Failing Test

```typescript
// cart.test.ts
import { calculateTotal } from './cart';

describe('calculateTotal', () => {
  it('returns 0 for empty cart', () => {
    const result = calculateTotal([]);
    expect(result).toBe(0);
  });
});
```

Run test - **FAILS** (function doesn't exist)

### GREEN: Minimal Implementation

```typescript
// cart.ts
export interface CartItem {
  price: number;
  quantity: number;
}

export function calculateTotal(items: CartItem[]): number {
  return 0;
}
```

Run test - **PASSES**

### REFACTOR: None Needed

Code is minimal, move to next cycle.

---

## Cycle 2: Single Item

### RED: Write Failing Test

```typescript
it('calculates total for single item', () => {
  const items = [{ price: 10, quantity: 1 }];
  const result = calculateTotal(items);
  expect(result).toBe(10);
});
```

Run test - **FAILS** (returns 0 instead of 10)

### GREEN: Minimal Implementation

```typescript
export function calculateTotal(items: CartItem[]): number {
  if (items.length === 0) return 0;
  return items[0].price * items[0].quantity;
}
```

Run test - **PASSES**

### REFACTOR: None Needed

Still too early to see patterns.

---

## Cycle 3: Multiple Items

### RED: Write Failing Test

```typescript
it('calculates total for multiple items', () => {
  const items = [
    { price: 10, quantity: 1 },
    { price: 20, quantity: 2 }
  ];
  const result = calculateTotal(items);
  expect(result).toBe(50); // 10 + 40
});
```

Run test - **FAILS** (returns 10 instead of 50)

### GREEN: Minimal Implementation

```typescript
export function calculateTotal(items: CartItem[]): number {
  let total = 0;
  for (const item of items) {
    total += item.price * item.quantity;
  }
  return total;
}
```

Run test - **PASSES**

### REFACTOR: Use Reduce

```typescript
export function calculateTotal(items: CartItem[]): number {
  return items.reduce((total, item) => total + item.price * item.quantity, 0);
}
```

Run all tests - **STILL PASS**

---

## Cycle 4: Percentage Discount

### RED: Write Failing Test

```typescript
interface Discount {
  type: 'percentage' | 'fixed';
  value: number;
}

it('applies percentage discount', () => {
  const items = [{ price: 100, quantity: 1 }];
  const discount: Discount = { type: 'percentage', value: 10 };

  const result = calculateTotal(items, discount);

  expect(result).toBe(90); // 100 - 10%
});
```

Run test - **FAILS** (function signature doesn't accept discount)

### GREEN: Minimal Implementation

```typescript
export interface Discount {
  type: 'percentage' | 'fixed';
  value: number;
}

export function calculateTotal(items: CartItem[], discount?: Discount): number {
  const subtotal = items.reduce((total, item) => total + item.price * item.quantity, 0);

  if (!discount) return subtotal;

  if (discount.type === 'percentage') {
    return subtotal - (subtotal * discount.value / 100);
  }

  return subtotal;
}
```

Run test - **PASSES**

### REFACTOR: Extract Discount Calculation

```typescript
function applyDiscount(subtotal: number, discount?: Discount): number {
  if (!discount) return subtotal;

  if (discount.type === 'percentage') {
    return subtotal * (1 - discount.value / 100);
  }

  return subtotal;
}

export function calculateTotal(items: CartItem[], discount?: Discount): number {
  const subtotal = items.reduce((total, item) => total + item.price * item.quantity, 0);
  return applyDiscount(subtotal, discount);
}
```

Run all tests - **STILL PASS**

---

## Cycle 5: Fixed Discount

### RED: Write Failing Test

```typescript
it('applies fixed discount', () => {
  const items = [{ price: 100, quantity: 1 }];
  const discount: Discount = { type: 'fixed', value: 15 };

  const result = calculateTotal(items, discount);

  expect(result).toBe(85); // 100 - 15
});
```

Run test - **FAILS** (returns 100, fixed discount not implemented)

### GREEN: Minimal Implementation

```typescript
function applyDiscount(subtotal: number, discount?: Discount): number {
  if (!discount) return subtotal;

  if (discount.type === 'percentage') {
    return subtotal * (1 - discount.value / 100);
  }

  if (discount.type === 'fixed') {
    return subtotal - discount.value;
  }

  return subtotal;
}
```

Run test - **PASSES**

### REFACTOR: Use Switch Statement

```typescript
function applyDiscount(subtotal: number, discount?: Discount): number {
  if (!discount) return subtotal;

  switch (discount.type) {
    case 'percentage':
      return subtotal * (1 - discount.value / 100);
    case 'fixed':
      return subtotal - discount.value;
    default:
      return subtotal;
  }
}
```

Run all tests - **STILL PASS**

---

## Cycle 6: Edge Case - Discount Exceeds Total

### RED: Write Failing Test

```typescript
it('returns 0 when fixed discount exceeds total', () => {
  const items = [{ price: 10, quantity: 1 }];
  const discount: Discount = { type: 'fixed', value: 20 };

  const result = calculateTotal(items, discount);

  expect(result).toBe(0); // Not negative
});
```

Run test - **FAILS** (returns -10)

### GREEN: Minimal Implementation

```typescript
function applyDiscount(subtotal: number, discount?: Discount): number {
  if (!discount) return subtotal;

  let result: number;

  switch (discount.type) {
    case 'percentage':
      result = subtotal * (1 - discount.value / 100);
      break;
    case 'fixed':
      result = subtotal - discount.value;
      break;
    default:
      result = subtotal;
  }

  return Math.max(0, result);
}
```

Run test - **PASSES**

### REFACTOR: None Needed

Code is clear and handles edge case.

---

## Final Code

```typescript
// cart.ts
export interface CartItem {
  price: number;
  quantity: number;
}

export interface Discount {
  type: 'percentage' | 'fixed';
  value: number;
}

function applyDiscount(subtotal: number, discount?: Discount): number {
  if (!discount) return subtotal;

  let result: number;

  switch (discount.type) {
    case 'percentage':
      result = subtotal * (1 - discount.value / 100);
      break;
    case 'fixed':
      result = subtotal - discount.value;
      break;
    default:
      result = subtotal;
  }

  return Math.max(0, result);
}

export function calculateTotal(items: CartItem[], discount?: Discount): number {
  const subtotal = items.reduce((total, item) => total + item.price * item.quantity, 0);
  return applyDiscount(subtotal, discount);
}
```

## Final Tests

```typescript
// cart.test.ts
import { calculateTotal, Discount } from './cart';

describe('calculateTotal', () => {
  it('returns 0 for empty cart', () => {
    expect(calculateTotal([])).toBe(0);
  });

  it('calculates total for single item', () => {
    const items = [{ price: 10, quantity: 1 }];
    expect(calculateTotal(items)).toBe(10);
  });

  it('calculates total for multiple items', () => {
    const items = [
      { price: 10, quantity: 1 },
      { price: 20, quantity: 2 }
    ];
    expect(calculateTotal(items)).toBe(50);
  });

  it('applies percentage discount', () => {
    const items = [{ price: 100, quantity: 1 }];
    const discount: Discount = { type: 'percentage', value: 10 };
    expect(calculateTotal(items, discount)).toBe(90);
  });

  it('applies fixed discount', () => {
    const items = [{ price: 100, quantity: 1 }];
    const discount: Discount = { type: 'fixed', value: 15 };
    expect(calculateTotal(items, discount)).toBe(85);
  });

  it('returns 0 when fixed discount exceeds total', () => {
    const items = [{ price: 10, quantity: 1 }];
    const discount: Discount = { type: 'fixed', value: 20 };
    expect(calculateTotal(items, discount)).toBe(0);
  });
});
```

## Key Takeaways

1. **Start simple** - Empty cart test first
2. **One behavior per cycle** - Single item, multiple items, each discount type
3. **Refactor only when patterns emerge** - Didn't extract `applyDiscount` until needed
4. **Edge cases last** - Handle discount exceeding total after core logic works
5. **Tests document behavior** - Reading tests explains what the function does
