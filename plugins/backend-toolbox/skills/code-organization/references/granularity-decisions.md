# Granularity Decision Guide

Extended decision trees and real-world examples for when to split or merge code.

## Decision Matrix

### Should I Split This File?

| Factor | Split | Keep Together |
|--------|-------|---------------|
| **Size** | > 300 lines | < 200 lines |
| **Responsibilities** | Multiple unrelated | Single focused |
| **Change frequency** | Parts change independently | All changes together |
| **Test isolation** | Hard to test parts in isolation | Easy to test as unit |
| **Team conflicts** | Frequent merge conflicts | Rare conflicts |
| **Naming** | Needs "and" or generic name | Clear, specific name |
| **Import count** | > 15 imports | < 10 imports |
| **Cognitive load** | Hard to find things | Easy to navigate |

**Decision:** If 3+ factors say "Split", split the file.

## Detailed Decision Trees

### Tree 1: File Size Decision

```
Is file > 500 lines?
├─ YES → MUST SPLIT (non-negotiable)
│         └─ Split by: responsibility, entity, or operation
└─ NO → Is file > 300 lines?
         ├─ YES → SHOULD SPLIT
         │         └─ Unless: extremely high cohesion (all code serves one purpose)
         └─ NO → Is file > 200 lines?
                  ├─ YES → CONSIDER SPLIT
                  │         └─ If: multiple responsibilities visible
                  └─ NO → KEEP (file is appropriately sized)
```

### Tree 2: Responsibility Decision

```
Can you describe the file in ONE sentence without "and"?
├─ NO → SPLIT by responsibility
│        └─ Each sentence becomes a file
└─ YES → Does the file mix different layers?
          ├─ YES → SPLIT by layer
          │        ├─ Data access → repository file
          │        ├─ Business logic → service file
          │        ├─ Validation → validator file
          │        └─ HTTP handling → controller file
          └─ NO → Does the file serve multiple consumers?
                   ├─ YES → CONSIDER SPLIT by consumer
                   └─ NO → KEEP (well-organized file)
```

### Tree 3: Change Reason Decision

```
When requirements change, does the WHOLE file change?
├─ YES → KEEP (high cohesion)
└─ NO → Do different PARTS change for different reasons?
         ├─ YES → SPLIT by change reason
         │        └─ Each reason = separate file
         └─ NO → Do changes span MULTIPLE logical sections?
                  ├─ YES → SPLIT by section
                  └─ NO → KEEP (acceptable coupling)
```

### Tree 4: The "Utils" Decision

```
Is this a utils/helpers/common file?
├─ YES → How many unrelated things are in it?
│         ├─ > 5 unrelated utilities → SPLIT by domain
│         │    └─ string-utils, date-utils, validation-utils, etc.
│         ├─ 3-5 utilities → CONSIDER SPLIT
│         │    └─ If any utility > 50 lines, extract it
│         └─ 1-2 utilities → KEEP but RENAME
│              └─ Name by purpose: `format-date.ts`, `parse-url.ts`
└─ NO → (Apply other decision trees)
```

## Real-World Examples

### Example 1: The God Service

**Before:** `order-service.ts` (600 lines)

```typescript
// order-service.ts - Does everything order-related
export class OrderService {
  // CRUD operations (150 lines)
  createOrder() { ... }
  updateOrder() { ... }
  deleteOrder() { ... }
  getOrder() { ... }

  // Validation (100 lines)
  validateOrder() { ... }
  validateLineItems() { ... }
  validateInventory() { ... }

  // Pricing (100 lines)
  calculateTotal() { ... }
  applyDiscounts() { ... }
  calculateTax() { ... }

  // Notifications (80 lines)
  sendConfirmation() { ... }
  sendShippingUpdate() { ... }

  // Reporting (100 lines)
  generateInvoice() { ... }
  getOrderStats() { ... }

  // Inventory integration (70 lines)
  reserveInventory() { ... }
  releaseInventory() { ... }
}
```

**After:** Split into focused files

```
orders/
├── order-service.ts        # Orchestration only (~100 lines)
├── order-repository.ts     # CRUD operations (~80 lines)
├── order-validator.ts      # Validation logic (~100 lines)
├── order-pricing.ts        # Price calculations (~100 lines)
├── order-notifier.ts       # Email/SMS notifications (~80 lines)
├── order-reporting.ts      # Reports and invoices (~100 lines)
└── inventory-integration.ts # Inventory operations (~70 lines)
```

**Decision rationale:**
- File > 500 lines → MUST SPLIT
- 6 distinct responsibilities → Split by responsibility
- Different change reasons → Each becomes a file

---

### Example 2: The Mixed Controller

**Before:** `user-controller.ts` (350 lines)

```typescript
// user-controller.ts - HTTP + Business Logic + Validation
export class UserController {
  async createUser(req) {
    // Input validation (30 lines)
    if (!req.body.email) throw new Error('Email required');
    if (!isValidEmail(req.body.email)) throw new Error('Invalid email');
    // ... more validation

    // Business logic (40 lines)
    const existingUser = await db.findByEmail(req.body.email);
    if (existingUser) throw new Error('User exists');
    const hashedPassword = await hash(req.body.password);
    // ... more logic

    // Database operations (20 lines)
    const user = await db.insert({...});

    // Response formatting (10 lines)
    return { id: user.id, email: user.email };
  }
  // ... 5 more methods with same pattern
}
```

**After:** Split by layer

```
users/
├── user-controller.ts      # HTTP handling only (~80 lines)
├── user-service.ts         # Business logic (~120 lines)
├── user-validator.ts       # Input validation (~60 lines)
└── user-repository.ts      # Database operations (~60 lines)
```

**Decision rationale:**
- Mixes HTTP, business logic, and data access → Split by layer
- Each method has 4 distinct concerns → Each concern becomes a file

---

### Example 3: The Feature File (Keep Together)

**Before/After:** `password-reset.ts` (180 lines)

```typescript
// password-reset.ts - Complete password reset feature
export class PasswordResetService {
  // Generate reset token (20 lines)
  async generateResetToken(email: string) { ... }

  // Validate token (15 lines)
  async validateToken(token: string) { ... }

  // Reset password (25 lines)
  async resetPassword(token: string, newPassword: string) { ... }

  // Send reset email (20 lines)
  private async sendResetEmail(email: string, token: string) { ... }

  // Clean expired tokens (15 lines)
  async cleanExpiredTokens() { ... }
}

// Token storage (30 lines)
interface ResetToken { ... }
const tokenStore = new Map<string, ResetToken>();

// Email template (20 lines)
function buildResetEmail(token: string) { ... }

// Helpers (15 lines)
function generateSecureToken() { ... }
function isTokenExpired(token: ResetToken) { ... }
```

**Decision: KEEP AS-IS**

- Size: 180 lines (under 200 threshold)
- Responsibility: Single feature (password reset)
- Change reason: All changes for same feature
- Cohesion: All code works together
- Name: Clear, specific, no "and"

---

### Example 4: The Utility Dump

**Before:** `utils.ts` (400 lines)

```typescript
// utils.ts - Random utilities
export function formatDate(date) { ... }           // 30 lines
export function parseDate(str) { ... }             // 20 lines
export function formatCurrency(amount) { ... }     // 25 lines
export function slugify(text) { ... }              // 15 lines
export function truncate(text, length) { ... }     // 10 lines
export function debounce(fn, delay) { ... }        // 20 lines
export function deepClone(obj) { ... }             // 40 lines
export function validateEmail(email) { ... }       // 15 lines
export function validatePhone(phone) { ... }       // 15 lines
export function validateUrl(url) { ... }           // 15 lines
export function generateId() { ... }               // 10 lines
export function hashPassword(password) { ... }     // 25 lines
export function comparePassword(plain, hash) { ... } // 15 lines
export function parseQueryString(qs) { ... }       // 30 lines
export function buildQueryString(params) { ... }   // 20 lines
// ... more random utilities
```

**After:** Split by domain

```
utils/
├── date-utils.ts           # formatDate, parseDate (50 lines)
├── format-utils.ts         # formatCurrency, slugify, truncate (50 lines)
├── function-utils.ts       # debounce, deepClone (60 lines)
├── validation-utils.ts     # validateEmail, validatePhone, validateUrl (45 lines)
├── password-utils.ts       # hashPassword, comparePassword (40 lines)
├── url-utils.ts            # parseQueryString, buildQueryString (50 lines)
└── id-utils.ts             # generateId (10 lines)
```

**Decision rationale:**
- > 5 unrelated utilities → SPLIT by domain
- Each group serves different consumers
- Related utilities change together

## Merge vs Split Summary

### When to SPLIT

1. **Size:** > 300 lines (soft), > 500 lines (hard)
2. **Multiple responsibilities:** Needs "and" to describe
3. **Mixed layers:** UI + logic + data in one file
4. **Different change reasons:** Parts change independently
5. **Team conflicts:** Frequent merge conflicts
6. **Testing difficulty:** Hard to test parts in isolation
7. **Import explosion:** > 15 imports suggests too many concerns

### When to KEEP TOGETHER

1. **High cohesion:** Everything serves one purpose
2. **Single feature:** Complete feature in one place
3. **Same change reason:** All code changes together
4. **Appropriate size:** Under 200 lines
5. **Clear naming:** Specific, no "and" or generics
6. **Easy testing:** Natural test boundary
7. **Low import count:** < 10 imports
