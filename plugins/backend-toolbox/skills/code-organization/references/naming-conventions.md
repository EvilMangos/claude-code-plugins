# Naming Conventions - Ports & Adapters

This reference covers the Ports & Adapters (Hexagonal) naming scheme that works identically in TypeScript and Python.

## Overview

The naming convention eliminates ambiguity by naming things based on their **role in the architecture**:

| Category             | Pattern                 | Examples                                       |
|----------------------|-------------------------|------------------------------------------------|
| Ports (abstractions) | Role nouns              | `EmailSender`, `UserRepository`, `Clock`       |
| Services             | `*Service` / `*UseCase` | `SignupService`, `CreateOrderService`          |
| Adapters             | Technology prefix       | `SesEmailSender`, `PostgresUserRepository`     |
| Data shapes          | Descriptive suffixes    | `SignupInput`, `UserDTO`, `CreateUserParams`   |

---

## 1. Ports (Abstractions) - Role Nouns

Name abstractions by **what they do**, not what they are. These are your DI tokens/contracts.

```typescript
// GOOD: Role-based port names
interface EmailSender {
  send(to: string, subject: string, body: string): Promise<void>;
}

interface UserRepository {
  save(user: User): Promise<void>;
  findById(id: string): Promise<User | null>;
}

interface Clock {
  now(): Date;
}

interface Logger {
  info(msg: string): void;
  error(msg: string, err?: Error): void;
}

interface PaymentGateway {
  charge(amount: Money, card: CardDetails): Promise<ChargeResult>;
}

interface JobQueue {
  enqueue(job: Job): Promise<void>;
}
```

```python
# Python equivalent (using Protocol or ABC)
from typing import Protocol

class EmailSender(Protocol):
    def send(self, to: str, subject: str, body: str) -> None: ...

class UserRepository(Protocol):
    def save(self, user: User) -> None: ...
    def find_by_id(self, id: str) -> User | None: ...

class Clock(Protocol):
    def now(self) -> datetime: ...
```

**Key principle:** The name describes the *capability*, not the implementation.

---

## 2. Business Logic - *Service / *UseCase

Technology-agnostic orchestrators that depend only on ports. These contain your business rules.

```typescript
// Services orchestrate business logic
class SignupService {
  constructor(
    private users: UserRepository,
    private emailSender: EmailSender,
    private clock: Clock
  ) {}

  async execute(input: SignupInput): Promise<SignupResult> {
    // Business logic here
  }
}

class GenerateReportService {
  constructor(
    private orders: OrderRepository,
    private formatter: ReportFormatter
  ) {}
}

class RefundSubscriptionService {
  constructor(
    private payments: PaymentGateway,
    private subscriptions: SubscriptionRepository
  ) {}
}
```

```python
# Python equivalent
class SignupService:
    def __init__(
        self,
        users: UserRepository,
        email_sender: EmailSender,
        clock: Clock
    ):
        self._users = users
        self._email_sender = email_sender
        self._clock = clock

    def execute(self, input: SignupInput) -> SignupResult:
        # Business logic here
        ...
```

**Key principle:** Services depend only on ports, never on adapters.

---

## 3. Adapters (Implementations) - Technology Prefix

Name implementations with their specific technology. These are the concrete classes that implement ports.

```typescript
// Adapters implement ports with specific technology
class SesEmailSender implements EmailSender {
  constructor(private sesClient: SESClient) {}

  async send(to: string, subject: string, body: string): Promise<void> {
    // AWS SES implementation
  }
}

class PostgresUserRepository implements UserRepository {
  constructor(private db: Pool) {}

  async save(user: User): Promise<void> {
    // PostgreSQL implementation
  }

  async findById(id: string): Promise<User | null> {
    // PostgreSQL implementation
  }
}

class StripePaymentGateway implements PaymentGateway {
  constructor(private stripe: Stripe) {}

  async charge(amount: Money, card: CardDetails): Promise<ChargeResult> {
    // Stripe implementation
  }
}

class SystemClock implements Clock {
  now(): Date {
    return new Date();
  }
}

class PinoLogger implements Logger {
  // Pino implementation
}
```

```python
# Python equivalent
class SesEmailSender:
    def __init__(self, ses_client: SESClient):
        self._ses_client = ses_client

    def send(self, to: str, subject: str, body: str) -> None:
        # AWS SES implementation
        ...

class PostgresUserRepository:
    def __init__(self, db: Connection):
        self._db = db

    def save(self, user: User) -> None:
        # PostgreSQL implementation
        ...
```

**Common adapter prefixes:**

| Technology    | Example Adapters                                    |
|---------------|-----------------------------------------------------|
| AWS           | `SesEmailSender`, `S3FileStorage`, `SqsJobQueue`    |
| Database      | `PostgresUserRepository`, `MongoOrderRepository`    |
| Payment       | `StripePaymentGateway`, `PayPalPaymentGateway`      |
| Logging       | `PinoLogger`, `WinstonLogger`, `ConsoleLogger`      |
| HTTP          | `AxiosHttpClient`, `FetchHttpClient`                |
| Cache         | `RedisCache`, `MemcachedCache`, `InMemoryCache`     |
| Time          | `SystemClock`, `FakeClock` (for testing)            |

---

## 4. Data Shapes - Suffixes, Not Prefixes

Use descriptive suffixes for data transfer objects. Never use prefixes like `I` or `T`.

```typescript
// GOOD: Suffix-based data shapes
interface SignupInput {
  email: string;
  password: string;
  name: string;
}

interface SignupResult {
  userId: string;
  confirmationToken: string;
}

interface UserDTO {
  id: string;
  email: string;
  name: string;
  createdAt: Date;
}

interface CreateUserParams {
  email: string;
  hashedPassword: string;
}

interface RefundReason {
  code: string;
  description: string;
}

// Domain events
interface OrderPlacedEvent {
  orderId: string;
  userId: string;
  total: Money;
  placedAt: Date;
}
```

```python
# Python equivalent (using dataclasses or Pydantic)
from dataclasses import dataclass
from pydantic import BaseModel

@dataclass
class SignupInput:
    email: str
    password: str
    name: str

@dataclass
class SignupResult:
    user_id: str
    confirmation_token: str

class UserDTO(BaseModel):
    id: str
    email: str
    name: str
    created_at: datetime
```

**Common suffixes:**

| Suffix     | Purpose                          | Example                          |
|------------|----------------------------------|----------------------------------|
| `Input`    | Service/use case input           | `SignupInput`, `CreateOrderInput`|
| `Result`   | Service/use case output          | `SignupResult`, `PaymentResult`  |
| `Params`   | Function/method parameters       | `CreateUserParams`, `QueryParams`|
| `DTO`      | Data transfer between layers     | `UserDTO`, `OrderDTO`            |
| `Event`    | Domain events                    | `OrderPlacedEvent`, `UserCreated`|
| `Config`   | Configuration objects            | `EmailSenderConfig`, `DbConfig`  |
| `Options`  | Optional settings                | `RetryOptions`, `CacheOptions`   |

---

## Anti-Patterns to Avoid

### Don't use prefixes

```typescript
// BAD: Hungarian notation prefixes
interface IUserRepository { }     // Don't use I prefix
interface IEmailSender { }        // Don't use I prefix
type TUser = { }                  // Don't use T prefix

// GOOD: Role nouns
interface UserRepository { }
interface EmailSender { }
type User = { }
```

### Don't name ports after implementations

```typescript
// BAD: Port named after implementation detail
interface MySQLUserRepository { }  // What if you switch to Postgres?
interface SendGridEmailer { }      // What if you switch to SES?

// GOOD: Port named after role
interface UserRepository { }       // Implementation-agnostic
interface EmailSender { }          // Implementation-agnostic
```

### Don't use vague names

```typescript
// BAD: Vague, unclear purpose
interface Service { }
interface Manager { }
interface Helper { }
interface Handler { }

// GOOD: Specific role
interface OrderValidator { }
interface PriceCalculator { }
interface ReceiptGenerator { }
```

### Don't mix concerns in names

```typescript
// BAD: Name implies multiple responsibilities
interface UserServiceAndRepository { }
interface EmailSenderAndLogger { }

// GOOD: Single responsibility per interface
interface UserRepository { }
interface EmailSender { }
interface Logger { }
```

---

## File Naming

Match file names to the primary export:

```
ports/
├── email-sender.ts          # interface EmailSender
├── user-repository.ts       # interface UserRepository
└── payment-gateway.ts       # interface PaymentGateway

adapters/
├── ses-email-sender.ts      # class SesEmailSender
├── postgres-user-repository.ts  # class PostgresUserRepository
└── stripe-payment-gateway.ts    # class StripePaymentGateway

services/
├── signup-service.ts        # class SignupService
└── create-order-service.ts  # class CreateOrderService
```

Use kebab-case for files, PascalCase for classes/interfaces.

---

## Summary

| Layer      | Naming Pattern        | Example                     | File Name                    |
|------------|-----------------------|-----------------------------|------------------------------|
| Port       | Role noun             | `EmailSender`               | `email-sender.ts`            |
| Adapter    | Technology + Role     | `SesEmailSender`            | `ses-email-sender.ts`        |
| Service    | Action + Service      | `SignupService`             | `signup-service.ts`          |
| Data Shape | Noun + Suffix         | `SignupInput`               | (in relevant module)         |

This convention:
- Eliminates name collisions (`EmailSender` port vs `SesEmailSender` adapter)
- Makes architecture visible in the code
- Works identically in TypeScript and Python
- Follows the Ports & Adapters (Hexagonal) pattern
