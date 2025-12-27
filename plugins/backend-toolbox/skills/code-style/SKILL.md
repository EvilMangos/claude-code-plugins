---
name: code-style
description: This skill should be used when the user asks about naming conventions, variable naming, function naming, type annotations, typing best practices, "how should I name this", "naming conventions", "TypeScript types", "Python types", "avoid any type", "type casting", "type safety", "interface naming", "class naming", "I prefix", "Hungarian notation", or needs guidance on consistent naming patterns, type annotation strategies, and type safety best practices.
version: 0.1.0
---

# Code Style

Comprehensive guidance on naming conventions, type annotations, and type safety best practices. Use this skill when naming code elements or working with type systems.

## Naming Conventions

### General Naming Principles

**Names should:**

- Describe **what** it does or **what** it represents, not **how**
- Be specific enough to predict behavior/contents
- Use consistent casing per language convention
- Avoid abbreviations unless universally understood

**Casing by language:**

| Language | Variables/Functions | Classes/Types | Constants | Files |
|----------|---------------------|---------------|-----------|-------|
| **TypeScript/JavaScript** | `camelCase` | `PascalCase` | `UPPER_SNAKE_CASE` | `kebab-case.ts` |
| **Python** | `snake_case` | `PascalCase` | `UPPER_SNAKE_CASE` | `snake_case.py` |
| **Go** | `camelCase` (private) / `PascalCase` (exported) | `PascalCase` | `PascalCase` or `camelCase` | `snake_case.go` |
| **Rust** | `snake_case` | `PascalCase` | `UPPER_SNAKE_CASE` | `snake_case.rs` |

### File Naming Rules

**File names should:**

- Describe what the file DOES, not what it CONTAINS
- Be specific enough to predict contents
- Avoid generic suffixes: `-utils`, `-helpers`, `-common`, `-misc`
- Match the primary export name

**Red flag names (require renaming):**

- `utils.ts`, `helpers.ts`, `common.ts`, `misc.ts`
- `*-stuff.ts`, `*-things.ts`
- `index.ts` with actual logic (not just re-exports)
- Names with "and" or multiple concepts

| Good (Focused) | Bad (Mixed) |
|----------------|-------------|
| `user-repository.ts` | `user-stuff.ts` |
| `order-validator.ts` | `order-helpers.ts` |
| `payment-gateway.ts` | `payment-utils.ts` |
| `email-template.ts` | `common.ts` |

### Ports & Adapters Naming Convention

When using hexagonal/ports & adapters architecture, follow these naming patterns:

| Category | Pattern | Examples |
|----------|---------|----------|
| Ports (abstractions) | Role nouns | `EmailSender`, `UserRepository`, `Clock` |
| Services | `*Service` / `*UseCase` | `SignupService`, `CreateOrderService` |
| Adapters | Technology prefix | `SesEmailSender`, `PostgresUserRepository` |
| Data shapes | Descriptive suffixes | `SignupInput`, `UserDTO`, `CreateUserParams` |

**Key rules:**

- No `I` prefix for interfaces (`UserRepository`, not `IUserRepository`)
- No `T` prefix for types (`User`, not `TUser`)
- Ports named by role, adapters named by technology

### Function and Method Naming

**Use verbs for actions:**

```typescript
// GOOD - verbs describe action
function calculateTotal(items: Item[]): number
function sendEmail(to: string, body: string): void
function validateOrder(order: Order): ValidationResult
function fetchUser(id: string): Promise<User>

// BAD - unclear what it does
function total(items: Item[]): number
function email(to: string, body: string): void
function order(order: Order): ValidationResult
```

**Boolean names should be questions:**

```typescript
// GOOD - reads as a question
const isActive: boolean
const hasPermission: boolean
const canEdit: boolean
const shouldRetry: boolean

// BAD - unclear it's a boolean
const active: boolean
const permission: boolean
const edit: boolean
```

**Getters/predicates naming:**

| Pattern | Use for | Example |
|---------|---------|---------|
| `getX` | Retrieving data | `getUser()`, `getConfig()` |
| `fetchX` | Async data retrieval | `fetchUser()`, `fetchOrders()` |
| `isX` | Boolean state check | `isValid()`, `isAdmin()` |
| `hasX` | Boolean existence check | `hasPermission()`, `hasItems()` |
| `canX` | Boolean capability check | `canEdit()`, `canDelete()` |
| `shouldX` | Boolean decision | `shouldRetry()`, `shouldNotify()` |
| `findX` | Search (may return null) | `findById()`, `findByEmail()` |

### Variable Naming

**Be specific, not generic:**

```typescript
// GOOD - specific names
const userEmail = user.email;
const orderTotal = calculateTotal(items);
const retryCount = 3;
const maxConnectionPoolSize = 10;

// BAD - generic names
const data = user.email;
const result = calculateTotal(items);
const num = 3;
const size = 10;
```

**Collection names should be plural:**

```typescript
// GOOD
const users: User[] = [];
const orderItems: OrderItem[] = [];
const activeConnections: Connection[] = [];

// BAD
const userList: User[] = [];  // redundant "List"
const user: User[] = [];      // singular for array
const orderItemArray: OrderItem[] = [];  // redundant "Array"
```

**Avoid abbreviations:**

| Avoid | Use Instead |
|-------|-------------|
| `usr` | `user` |
| `msg` | `message` |
| `btn` | `button` |
| `cfg` | `config` |
| `err` | `error` |
| `req`, `res` | `request`, `response` |
| `ctx` | `context` |
| `idx`, `i`, `j` | `index`, `userIndex`, or descriptive name |

**Exception:** Universally understood abbreviations are acceptable: `id`, `url`, `api`, `http`, `html`, `css`, `json`, `xml`.

## Type Safety

### Type Casting Guidelines

**Avoid type casting whenever possible.** Type casting (`as`, `<Type>`, or `# type: ignore`) bypasses the type system's safety guarantees. Use casting only as a last resort when:

1. **Working with external libraries** that have incomplete or incorrect type definitions
2. **Type narrowing limitations** where the compiler can't infer what you've proven through runtime checks
3. **Test doubles/mocks** where you need to satisfy interface requirements with partial implementations

**Before casting, try these alternatives:**

| Instead of | Try |
|------------|-----|
| `value as Type` | Type guards, discriminated unions, or generics |
| `obj as any` | Properly typed interfaces or unknown with validation |
| `// @ts-ignore` | Fix the underlying type issue |
| `# type: ignore` | Add proper type annotations |

```typescript
// BAD - Casting to silence the compiler
const user = response.data as User;

// GOOD - Runtime validation with type narrowing
function isUser(data: unknown): data is User {
  return typeof data === 'object' && data !== null && 'id' in data;
}
const user = isUser(response.data) ? response.data : null;
```

**Warning:** Every type cast is a potential runtime error waiting to happen. When you cast, you're telling the compiler "trust me" - make sure you're right.

### Avoid `any` Type

**Never use `any` (TypeScript) or untyped variables (Python).** The `any` type disables all type checking and defeats the purpose of using a typed language.

**TypeScript - alternatives to `any`:**

| Instead of | Use |
|------------|-----|
| `any` | `unknown` + type guards for truly unknown data |
| `any[]` | `unknown[]` or generic `T[]` |
| `Record<string, any>` | `Record<string, unknown>` or proper interface |
| `Function` | Specific function signature `(arg: Type) => ReturnType` |
| `object` | Specific interface or `Record<string, unknown>` |

```typescript
// BAD
function process(data: any): any {
  return data.value;
}

// GOOD
function process<T extends { value: unknown }>(data: T): T['value'] {
  return data.value;
}

// BAD - parsing JSON
const config = JSON.parse(text) as any;

// GOOD - parsing JSON with validation
const parsed: unknown = JSON.parse(text);
if (isConfig(parsed)) {
  const config = parsed; // now typed as Config
}
```

**Python - always use type annotations:**

| Instead of | Use |
|------------|-----|
| No annotation | Explicit type: `def fn(x: int) -> str:` |
| `Any` | `object` for true any, or specific Union types |
| `Dict` (untyped) | `dict[str, int]` or `TypedDict` |
| `List` (untyped) | `list[Item]` with specific element type |
| `Callable` (untyped) | `Callable[[int, str], bool]` with signature |

```python
# BAD
def process(data):
    return data["value"]

# GOOD
from typing import TypedDict

class DataWithValue(TypedDict):
    value: str

def process(data: DataWithValue) -> str:
    return data["value"]

# BAD - using Any
from typing import Any
def handle(item: Any) -> Any:
    return item

# GOOD - using generics
from typing import TypeVar
T = TypeVar('T')
def handle(item: T) -> T:
    return item
```

**When `any`/`Any` might be acceptable (rare):**

1. **Migrating legacy code** - as a temporary step with a TODO to fix
2. **Third-party library gaps** - when type stubs don't exist (prefer contributing stubs)
3. **Metaprogramming** - decorators or dynamic proxies that genuinely work with any type

Even in these cases, isolate `any` to the smallest possible scope and add runtime validation at boundaries.

### Type Annotation Best Practices

**Always annotate:**

- Function parameters and return types
- Class properties
- Module-level variables
- Complex expressions where inference isn't obvious

**Let inference work for:**

- Local variables with obvious types from initialization
- Lambda/arrow function parameters when passed to well-typed higher-order functions
- Literal assignments

```typescript
// GOOD - annotate function signatures
function calculateTax(amount: number, rate: number): number {
  const result = amount * rate;  // inference is fine here
  return result;
}

// GOOD - annotate when inference isn't obvious
const config: AppConfig = loadConfig();
const handler: RequestHandler = (req, res) => { /* ... */ };

// UNNECESSARY - over-annotation
const count: number = 0;  // type is obvious from literal
const name: string = "John";  // type is obvious from literal
```

## Quick Reference Card

### Naming

- Use descriptive, specific names
- Follow language casing conventions
- No Hungarian notation (`strName`, `iCount`)
- No `I` prefix for interfaces, no `T` prefix for types
- Verbs for functions, nouns for variables
- Boolean names should read as questions (`isActive`, `hasPermission`)

### Type Safety

- Never use `any` - use `unknown` + type guards
- Avoid type casting - use runtime validation
- Annotate function signatures explicitly
- Let inference handle obvious local variables
- Every `as` cast is a potential bug

### Red Flags

- `any` type anywhere
- Type assertions (`as Type`) without runtime checks
- `// @ts-ignore` or `# type: ignore`
- Generic variable names (`data`, `result`, `temp`)
- Abbreviated names (`usr`, `cfg`, `msg`)
- Hungarian notation (`strName`, `arrItems`)

## Related Skills

- **code-organization** - File structure, module boundaries, and when to split code
- **design-patterns** - Patterns for structuring code (SRP, DIP, layers)
- **refactoring-patterns** - Mechanics for renaming and restructuring code
- **code-review-checklist** - Verify naming and type safety during review
