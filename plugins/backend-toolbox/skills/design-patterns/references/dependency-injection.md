# Dependency Injection - Detailed Reference

This reference covers dependency injection concepts, injection patterns, container usage, and testing implications.

For naming conventions (ports, adapters, services, data shapes), see `code-organization/references/naming-conventions.md`.

---

## What is Dependency Injection?

Dependency Injection (DI) is a technique where objects receive their dependencies from external sources rather than
creating them internally. It's the practical application of the Dependency Inversion Principle (DIP).

**Without DI:**

```typescript
class OrderService {
  private repository = new PostgresOrderRepository(); // Hard-coded dependency
  private emailSender = new SendGridEmailSender();    // Hard-coded dependency
}
```

**With DI:**

```typescript
class OrderService {
  constructor(
    private repository: OrderRepository,  // Injected port
    private emailSender: EmailSender      // Injected port
  ) {}
}
```

---

## Benefits of Dependency Injection

### 1. Testability

```typescript
// Easy to test with mocks
describe("OrderService", () => {
  it("should save order and send email", async () => {
    const mockRepo = { save: jest.fn() };
    const mockEmailSender = { send: jest.fn() };

    const service = new OrderService(mockRepo, mockEmailSender);
    await service.createOrder(testOrder);

    expect(mockRepo.save).toHaveBeenCalledWith(testOrder);
    expect(mockEmailSender.send).toHaveBeenCalled();
  });
});
```

### 2. Flexibility

```typescript
// Swap implementations based on environment
const repository =
  process.env.NODE_ENV === "test"
    ? new InMemoryOrderRepository()
    : new PostgresOrderRepository();

const service = new OrderService(repository, emailSender);
```

### 3. Decoupling

```typescript
// OrderService doesn't know or care about:
// - What database is used
// - How emails are sent
// - What logging framework is used
class OrderService {
  constructor(
    private repository: OrderRepository,
    private emailSender: EmailSender,
    private logger: Logger
  ) {}
}
```

### 4. Single Responsibility

Dependencies are created and configured elsewhere, so classes focus on their core logic.

---

## Injection Patterns

### 1. Constructor Injection (Preferred)

Dependencies are provided through the constructor.

```typescript
class CreateUserService {
  constructor(
    private userRepository: UserRepository,
    private passwordHasher: PasswordHasher,
    private emailSender: EmailSender
  ) {}

  async execute(input: CreateUserInput): Promise<User> {
    const hashedPassword = await this.passwordHasher.hash(input.password);
    const user = new User(input.name, input.email, hashedPassword);
    await this.userRepository.save(user);
    await this.emailSender.send(user.email, "Welcome!", "Thanks for signing up");
    return user;
  }
}
```

**Advantages:**

- Dependencies are explicit and required
- Object is fully initialized after construction
- Easy to see all dependencies at a glance
- Immutable dependencies (can use `readonly`)

**Best practice:** Use constructor injection for required dependencies.

### 2. Setter/Property Injection

Dependencies are provided through setters or public properties.

```typescript
class ReportGenerator {
  private formatter: ReportFormatter;

  setFormatter(formatter: ReportFormatter): void {
    this.formatter = formatter;
  }

  generate(data: ReportData): Report {
    if (!this.formatter) {
      throw new Error("Formatter not set");
    }
    return this.formatter.format(data);
  }
}

// Usage
const generator = new ReportGenerator();
generator.setFormatter(new PdfReportFormatter());
generator.generate(data);
```

**Advantages:**

- Can change dependencies after construction
- Useful for optional dependencies

**Disadvantages:**

- Object may be in invalid state
- Dependencies not obvious from constructor
- Order of method calls matters

**Best practice:** Use setter injection for optional dependencies.

### 3. Method Injection

Dependencies are provided through method parameters.

```typescript
class DataProcessor {
  process(data: RawData, validator: DataValidator): ProcessedData {
    if (!validator.validate(data)) {
      throw new ValidationError("Invalid data");
    }
    // Process data...
  }
}

// Usage
const processor = new DataProcessor();
processor.process(data, new StrictDataValidator());
processor.process(data, new LenientDataValidator());
```

**Advantages:**

- Different dependencies per method call
- Useful when dependency varies by context

**Best practice:** Use method injection when dependency varies per call.

### 4. Interface Injection

Class implements an interface that defines setter method.

```typescript
interface LoggerAware {
  setLogger(logger: Logger): void;
}

class OrderService implements LoggerAware {
  private logger: Logger;

  setLogger(logger: Logger): void {
    this.logger = logger;
  }
}

// Container can inject logger into any LoggerAware class
function injectLogger(target: LoggerAware, logger: Logger): void {
  target.setLogger(logger);
}
```

**Best practice:** Use interface injection for cross-cutting concerns.

---

## Dependency Injection Containers

A DI container (IoC container) automates dependency creation and injection.

### Basic Container Implementation

```typescript
class Container {
  private services: Map<string, any> = new Map();
  private factories: Map<string, () => any> = new Map();

  // Register a singleton instance
  register<T>(token: string, instance: T): void {
    this.services.set(token, instance);
  }

  // Register a factory for transient instances
  registerFactory<T>(token: string, factory: () => T): void {
    this.factories.set(token, factory);
  }

  // Resolve a dependency
  resolve<T>(token: string): T {
    if (this.services.has(token)) {
      return this.services.get(token);
    }
    if (this.factories.has(token)) {
      return this.factories.get(token)!();
    }
    throw new Error(`Service not found: ${token}`);
  }
}

// Usage
const container = new Container();
container.register("config", new AppConfig());
container.registerFactory("logger", () => new PinoLogger());

const config = container.resolve<AppConfig>("config");
const logger = container.resolve<Logger>("logger");
```

### Decorator-Based DI (TypeScript)

Using decorators with reflect-metadata:

```typescript
import "reflect-metadata";

const INJECTABLE_KEY = Symbol("injectable");
const INJECT_KEY = Symbol("inject");

// Mark class as injectable
function Injectable(): ClassDecorator {
  return (target) => {
    Reflect.defineMetadata(INJECTABLE_KEY, true, target);
  };
}

// Mark parameter for injection
function Inject(token: string): ParameterDecorator {
  return (target, propertyKey, parameterIndex) => {
    const existing = Reflect.getMetadata(INJECT_KEY, target) || [];
    existing.push({ index: parameterIndex, token });
    Reflect.defineMetadata(INJECT_KEY, existing, target);
  };
}

@Injectable()
class CreateUserService {
  constructor(
    @Inject("UserRepository") private repo: UserRepository,
    @Inject("Logger") private logger: Logger
  ) {}
}
```

### Popular DI Containers

**TypeScript/JavaScript:**

- **InversifyJS** - Full-featured, decorator-based
- **TSyringe** - Lightweight, Microsoft
- **TypeDI** - Simple and powerful
- **Awilix** - Function-based, no decorators

**Framework-Integrated:**

- **NestJS** - Built-in DI container
- **Angular** - Hierarchical injector
- **Spring (Java)** - ApplicationContext

---

## Lifetimes and Scopes

### Singleton

One instance for entire application lifetime.

```typescript
container.registerSingleton(DatabaseConnection);

// Same instance every time
const db1 = container.resolve(DatabaseConnection);
const db2 = container.resolve(DatabaseConnection);
// db1 === db2
```

**Use for:**

- Configuration
- Database connection pools
- Caches
- Stateless services

### Transient

New instance for every resolution.

```typescript
container.registerTransient(RequestLogger);

// New instance every time
const logger1 = container.resolve(RequestLogger);
const logger2 = container.resolve(RequestLogger);
// logger1 !== logger2
```

**Use for:**

- Stateful services
- Services with request-specific data
- Services that shouldn't be shared

### Scoped

One instance per scope (e.g., per HTTP request).

```typescript
// Pseudo-code for request scope
app.use((req, res, next) => {
  req.scope = container.createScope();
  next();
});

// Within request handler
const userService = req.scope.resolve(CreateUserService);
// Same instance for this request, different for other requests
```

**Use for:**

- Per-request services
- Unit of work patterns
- Services with request-specific state

---

## Best Practices

### 1. Depend on Abstractions (Ports)

```typescript
// GOOD: Depend on port (interface)
class OrderService {
  constructor(private repository: OrderRepository) {}
}

// BAD: Depend on concrete adapter
class OrderService {
  constructor(private repository: PostgresOrderRepository) {}
}
```

### 2. Locate Ports in a Dedicated Layer

**Critical**: Ports must NOT live in the consumer's module or the adapter's module. They belong in a separate layer.

**Why this matters:**

- Port with consumer → adapter gains unwanted dependency on consumer
- Port with adapter → consumer depends on adapter's module (defeats DIP)
- Port in dedicated layer → true decoupling achieved

**Single Package/Module Pattern:**

```
src/
├── ports/                  # Ports layer - interfaces only
│   ├── order-repository.ts # interface OrderRepository
│   ├── payment-gateway.ts  # interface PaymentGateway
│   └── email-sender.ts     # interface EmailSender
├── domain/                 # High-level business logic
│   └── order-service.ts    # depends on ports/*, NOT on adapters/*
└── adapters/               # Implementations
    ├── postgres-order-repository.ts  # implements OrderRepository
    ├── stripe-payment-gateway.ts     # implements PaymentGateway
    └── sendgrid-email-sender.ts      # implements EmailSender
```

```typescript
// ports/order-repository.ts
export interface OrderRepository {
  save(order: Order): Promise<void>;
  findById(id: string): Promise<Order | null>;
}

// domain/order-service.ts - depends ONLY on ports
import { OrderRepository } from '../ports/order-repository';
import { PaymentGateway } from '../ports/payment-gateway';

class OrderService {
  constructor(
    private repository: OrderRepository,   // Port
    private payment: PaymentGateway        // Port
  ) {}
}

// adapters/postgres-order-repository.ts - implements port
import { OrderRepository } from '../ports/order-repository';

class PostgresOrderRepository implements OrderRepository {
  // Implementation details...
}
```

**Monorepo Pattern:**

When dependencies cross package/repository boundaries, create a dedicated ports package:

```
monorepo/
├── packages/
│   ├── ports/               # Shared ports package
│   │   ├── package.json     # @myorg/ports
│   │   └── src/
│   │       ├── order-repository.ts
│   │       ├── payment-gateway.ts
│   │       └── index.ts
│   ├── order-service/       # Consumer package
│   │   ├── package.json     # depends on @myorg/ports
│   │   └── src/
│   │       └── order-service.ts
│   └── postgres-adapter/    # Adapter package
│       ├── package.json     # depends on @myorg/ports
│       └── src/
│           └── postgres-order-repository.ts
```

```json
// packages/order-service/package.json
{
  "name": "@myorg/order-service",
  "dependencies": {
    "@myorg/ports": "workspace:*"  // Only depends on ports
  }
}

// packages/postgres-adapter/package.json
{
  "name": "@myorg/postgres-adapter",
  "dependencies": {
    "@myorg/ports": "workspace:*"  // Implements ports
  }
}
```

**Hexagonal Architecture:**

In hexagonal (ports and adapters) architecture:

- **Ports** (interfaces) live in the **domain/core** layer
- **Adapters** depend on the domain and implement its ports
- This is intentional: the domain defines what it needs, adapters conform to it

```
src/
├── domain/                 # Core domain - owns the ports
│   ├── model/
│   │   └── order.ts
│   └── ports/              # Ports ARE in domain (hexagonal pattern)
│       ├── order-repository.ts
│       └── payment-gateway.ts
├── application/            # Use cases / services
│   └── create-order-service.ts
└── adapters/               # Adapters implement domain ports
    ├── driven/             # Secondary/driven adapters
    │   ├── postgres-order-repository.ts
    │   └── stripe-payment-gateway.ts
    └── driving/            # Primary/driving adapters
        └── rest-api-adapter.ts
```

In hexagonal architecture, the domain is the center and everything points inward. Adapters depend on the domain, not the other way around.

### 3. Avoid Service Locator Anti-Pattern

```typescript
// BAD: Service locator - hides dependencies
class OrderService {
  createOrder(order: Order): void {
    const repo = ServiceLocator.get("OrderRepository");
    const emailSender = ServiceLocator.get("EmailSender");
    // Dependencies not visible from constructor
  }
}

// GOOD: Constructor injection - explicit dependencies
class OrderService {
  constructor(private repo: OrderRepository, private emailSender: EmailSender) {}
}
```

### 4. Keep Constructors Simple

```typescript
// BAD: Logic in constructor
class CreateUserService {
  constructor(private repo: UserRepository) {
    this.warmUpCache(); // Side effect
    this.validateConnection(); // Can throw
  }
}

// GOOD: Simple assignment only
class CreateUserService {
  constructor(private repo: UserRepository) {}

  async initialize(): Promise<void> {
    await this.warmUpCache();
    await this.validateConnection();
  }
}
```

### 5. Avoid Circular Dependencies

```typescript
// BAD: Circular dependency
class ServiceA {
  constructor(private serviceB: ServiceB) {}
}

class ServiceB {
  constructor(private serviceA: ServiceA) {} // Circular!
}

// GOOD: Break cycle with port or events
interface NotificationSender {
  notify(message: string): void;
}

class ServiceA implements NotificationSender {
  constructor(private serviceB: ServiceB) {}
  notify(message: string): void {
    /* ... */
  }
}

class ServiceB {
  constructor(private notifier: NotificationSender) {}
}
```

### 6. Inject What You Need

```typescript
// BAD: Injecting container itself
class OrderService {
  constructor(private container: Container) {
    // Hides actual dependencies
  }

  createOrder(): void {
    const repo = this.container.resolve("repo");
  }
}

// GOOD: Inject specific dependencies
class OrderService {
  constructor(private repo: OrderRepository) {}
}
```

### 7. Use Factory for Complex Creation

```typescript
// When creation logic is complex
interface UserServiceFactory {
  create(tenantId: string): CreateUserService;
}

class TenantAwareUserServiceFactory implements UserServiceFactory {
  constructor(private connectionPool: ConnectionPool, private config: AppConfig) {}

  create(tenantId: string): CreateUserService {
    const connection = this.connectionPool.getForTenant(tenantId);
    const repo = new PostgresUserRepository(connection);
    return new CreateUserService(repo, this.config);
  }
}

// Inject factory, not service
class TenantController {
  constructor(private userServiceFactory: UserServiceFactory) {}

  handleRequest(req: Request): void {
    const service = this.userServiceFactory.create(req.tenantId);
    // Use service...
  }
}
```

---

## Testing with DI

### Unit Testing with Mocks

```typescript
describe("OrderService", () => {
  let service: OrderService;
  let mockRepo: jest.Mocked<OrderRepository>;
  let mockEmailSender: jest.Mocked<EmailSender>;

  beforeEach(() => {
    mockRepo = {
      save: jest.fn(),
      findById: jest.fn(),
    };
    mockEmailSender = {
      send: jest.fn(),
    };

    service = new OrderService(mockRepo, mockEmailSender);
  });

  it("should save order and send confirmation", async () => {
    const order = new Order("123", []);

    await service.createOrder(order);

    expect(mockRepo.save).toHaveBeenCalledWith(order);
    expect(mockEmailSender.send).toHaveBeenCalledWith(
      expect.objectContaining({ orderId: "123" })
    );
  });

  it("should not send email if save fails", async () => {
    mockRepo.save.mockRejectedValue(new Error("DB error"));

    await expect(service.createOrder(new Order("123", []))).rejects.toThrow(
      "DB error"
    );

    expect(mockEmailSender.send).not.toHaveBeenCalled();
  });
});
```

### Integration Testing with Test Doubles

```typescript
describe("OrderService Integration", () => {
  let service: OrderService;
  let testRepo: InMemoryOrderRepository;
  let testEmailSender: SpyEmailSender;

  beforeEach(() => {
    testRepo = new InMemoryOrderRepository();
    testEmailSender = new SpyEmailSender();

    service = new OrderService(testRepo, testEmailSender);
  });

  it("should persist order", async () => {
    const order = new Order("123", [item1, item2]);

    await service.createOrder(order);

    const saved = await testRepo.findById("123");
    expect(saved).toEqual(order);
    expect(testEmailSender.sentEmails).toHaveLength(1);
  });
});
```

---

## Common Mistakes

### 1. Over-Injection

```typescript
// BAD: Too many dependencies (> 4-5 is a smell)
class GodService {
  constructor(
    private repo1: Repository1,
    private repo2: Repository2,
    private service1: Service1,
    private service2: Service2,
    private logger: Logger,
    private config: AppConfig,
    private cache: Cache,
    private validator: Validator
  ) // ... more
  {}
}

// GOOD: Split into focused classes
class OrderCreator {
  constructor(
    private repo: OrderRepository,
    private validator: OrderValidator
  ) {}
}

class OrderNotifier {
  constructor(private emailSender: EmailSender, private smsSender: SmsSender) {}
}
```

### 2. Injecting Primitives Directly

```typescript
// BAD: Primitive parameters mixed with services
class SendGridEmailSender {
  constructor(
    private smtpHost: string, // Primitive
    private smtpPort: number, // Primitive
    private logger: Logger    // Service
  ) {}
}

// GOOD: Group primitives into config object
interface EmailSenderConfig {
  smtpHost: string;
  smtpPort: number;
  fromAddress: string;
}

class SendGridEmailSender {
  constructor(private config: EmailSenderConfig, private logger: Logger) {}
}
```

### 3. Temporal Coupling

```typescript
// BAD: Must call init() before use
class SomeService {
  constructor(private repo: SomeRepository) {}

  init(): void {
    this.connection = this.repo.connect();  // Required before use
  }

  doWork(): void {
    this.connection.query(...);  // Fails if init() not called
  }
}

// GOOD: Fully initialized after construction
class SomeService {
  constructor(private connection: DatabaseConnection) {}

  doWork(): void {
    this.connection.query(...);  // Always works
  }
}
```

---

## Summary

| Pattern               | When to Use                            |
|-----------------------|----------------------------------------|
| Constructor Injection | Required dependencies (default choice) |
| Setter Injection      | Optional dependencies                  |
| Method Injection      | Per-call varying dependencies          |
| Factory Injection     | Complex/contextual creation            |

| Lifetime  | When to Use                 |
|-----------|-----------------------------|
| Singleton | Stateless, shared resources |
| Transient | Stateful, per-use instances |
| Scoped    | Per-request, unit of work   |
