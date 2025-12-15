# Domain-Driven Design (DDD) - Comprehensive Reference

Domain-Driven Design is an approach to software development that centers the design on the core business domain. It provides both strategic patterns (for organizing large systems) and tactical patterns (for modeling domain logic).

## When to Use DDD

**Good fit:**
- Complex business logic with many rules
- Domain experts available for collaboration
- Long-lived projects that will evolve
- Multiple bounded contexts / subdomains
- Team needs shared understanding of domain

**Poor fit:**
- Simple CRUD applications
- Technical/infrastructure-focused systems
- Short-term or throwaway projects
- No domain expert access
- Purely data-centric applications

---

## Strategic Patterns

Strategic patterns help organize large systems and define boundaries between different parts of the domain.

### Bounded Context

A bounded context is a boundary within which a particular domain model is defined and applicable. Different contexts may have different models for the same real-world concept.

```
┌─────────────────────────────────────────────────────────────────┐
│                        E-Commerce System                         │
├─────────────────────┬─────────────────────┬─────────────────────┤
│   Sales Context     │  Shipping Context   │  Billing Context    │
├─────────────────────┼─────────────────────┼─────────────────────┤
│ Customer:           │ Customer:           │ Customer:           │
│ - name              │ - shippingAddress   │ - billingAddress    │
│ - email             │ - deliveryPrefs     │ - paymentMethods    │
│ - purchaseHistory   │                     │ - creditLimit       │
├─────────────────────┼─────────────────────┼─────────────────────┤
│ Order:              │ Shipment:           │ Invoice:            │
│ - lineItems         │ - packages          │ - lineItems         │
│ - discounts         │ - carrier           │ - taxes             │
│ - status            │ - trackingNumber    │ - paymentStatus     │
└─────────────────────┴─────────────────────┴─────────────────────┘
```

**Key principles:**
- Each context has its own ubiquitous language
- Models don't leak across context boundaries
- Contexts communicate through well-defined interfaces
- Same real-world concept can have different representations

**Identifying bounded contexts:**
- Look for linguistic boundaries (different terms for same thing)
- Organizational boundaries (different teams)
- Different business capabilities
- Different rates of change

### Ubiquitous Language

A shared vocabulary between developers and domain experts, used consistently in code, documentation, and conversation.

```typescript
// BAD: Technical jargon, not domain language
class DataProcessor {
  processRecords(records: Record[]): void {
    records.forEach(r => {
      if (r.flag === 1) {
        this.handler.handle(r);
      }
    });
  }
}

// GOOD: Ubiquitous language from the domain
class OrderFulfillmentService {
  fulfillPendingOrders(orders: Order[]): void {
    orders.forEach(order => {
      if (order.isReadyForFulfillment()) {
        this.warehouse.shipOrder(order);
      }
    });
  }
}
```

**Building ubiquitous language:**
- Work closely with domain experts
- Use domain terms in code (class names, methods, variables)
- Refactor code when language evolves
- Document the glossary
- Challenge ambiguous terms
- Avoid technical jargon in domain layer

### Context Mapping

Defines relationships between bounded contexts.

| Pattern | Description | When to Use |
|---------|-------------|-------------|
| **Shared Kernel** | Two contexts share a subset of the model | Tightly coupled teams, shared core concepts |
| **Customer-Supplier** | Upstream context provides what downstream needs | Clear dependency direction |
| **Conformist** | Downstream adopts upstream's model as-is | No influence over upstream |
| **Anti-Corruption Layer** | Translation layer protects from external models | Integrating legacy/external systems |
| **Open Host Service** | Context exposes well-defined API | Many consumers |
| **Published Language** | Shared interchange format (JSON schema, etc.) | Integration between systems |
| **Separate Ways** | No integration, contexts are independent | No meaningful relationship |
| **Partnership** | Two contexts cooperate on integration | Mutual dependency, aligned teams |

### Anti-Corruption Layer (ACL)

A translation layer that protects your domain model from external or legacy models.

```typescript
// External legacy system with poor model
interface LegacyCustomerDTO {
  cust_id: string;
  cust_nm: string;
  addr_ln_1: string;
  addr_ln_2: string;
  cty: string;
  st: string;
  zp: string;
}

// Our clean domain model
class Customer {
  constructor(
    public readonly id: CustomerId,
    public readonly name: CustomerName,
    public readonly address: Address
  ) {}
}

// Anti-corruption layer translates between models
class CustomerTranslator {
  toDomain(legacy: LegacyCustomerDTO): Customer {
    return new Customer(
      new CustomerId(legacy.cust_id),
      new CustomerName(legacy.cust_nm),
      new Address(
        legacy.addr_ln_1,
        legacy.addr_ln_2,
        legacy.cty,
        legacy.st,
        legacy.zp
      )
    );
  }

  toLegacy(customer: Customer): LegacyCustomerDTO {
    return {
      cust_id: customer.id.value,
      cust_nm: customer.name.value,
      addr_ln_1: customer.address.line1,
      addr_ln_2: customer.address.line2,
      cty: customer.address.city,
      st: customer.address.state,
      zp: customer.address.zipCode
    };
  }
}

// ACL facade hides the legacy system
class CustomerGateway {
  constructor(
    private legacyApi: LegacyCustomerApi,
    private translator: CustomerTranslator
  ) {}

  async findById(id: CustomerId): Promise<Customer | null> {
    const legacyData = await this.legacyApi.getCustomer(id.value);
    if (!legacyData) return null;
    return this.translator.toDomain(legacyData);
  }

  async save(customer: Customer): Promise<void> {
    const legacyData = this.translator.toLegacy(customer);
    await this.legacyApi.updateCustomer(legacyData);
  }
}
```

**When to use ACL:**
- Integrating with legacy systems
- Consuming third-party APIs
- Protecting from upstream model changes
- Isolating technical debt

---

## Tactical Patterns

Tactical patterns help model the domain within a bounded context.

### Entity

An object defined by its identity rather than its attributes. Identity persists across time and state changes.

```typescript
class Order {
  private _id: OrderId;
  private _status: OrderStatus;
  private _lineItems: LineItem[];
  private _createdAt: Date;

  constructor(id: OrderId) {
    this._id = id;
    this._status = OrderStatus.Draft;
    this._lineItems = [];
    this._createdAt = new Date();
  }

  get id(): OrderId { return this._id; }

  addLineItem(product: Product, quantity: number): void {
    if (this._status !== OrderStatus.Draft) {
      throw new Error('Cannot modify non-draft order');
    }
    this._lineItems.push(new LineItem(product.id, quantity, product.price));
  }

  submit(): void {
    if (this._lineItems.length === 0) {
      throw new Error('Cannot submit empty order');
    }
    this._status = OrderStatus.Submitted;
  }

  // Identity-based equality
  equals(other: Order): boolean {
    return this._id.equals(other._id);
  }
}
```

**Entity characteristics:**
- Has unique identity (usually a dedicated ID type)
- Identity remains constant through state changes
- Equality based on identity, not attributes
- Lifecycle tracking matters
- Encapsulates business rules

**Entity vs Data Object:**
```typescript
// Entity - has identity and behavior
class Customer {
  private _id: CustomerId;
  private _status: CustomerStatus;

  deactivate(): void {
    if (this._status === CustomerStatus.Deactivated) {
      throw new Error('Already deactivated');
    }
    this._status = CustomerStatus.Deactivated;
  }
}

// Data object - just holds data
interface CustomerDTO {
  id: string;
  status: string;
}
```

### Value Object

An immutable object defined by its attributes, with no conceptual identity.

```typescript
class Money {
  constructor(
    public readonly amount: number,
    public readonly currency: Currency
  ) {
    if (amount < 0) {
      throw new Error('Amount cannot be negative');
    }
  }

  add(other: Money): Money {
    if (!this.currency.equals(other.currency)) {
      throw new Error('Cannot add different currencies');
    }
    return new Money(this.amount + other.amount, this.currency);
  }

  subtract(other: Money): Money {
    if (!this.currency.equals(other.currency)) {
      throw new Error('Cannot subtract different currencies');
    }
    return new Money(this.amount - other.amount, this.currency);
  }

  multiply(factor: number): Money {
    return new Money(this.amount * factor, this.currency);
  }

  // Value-based equality
  equals(other: Money): boolean {
    return this.amount === other.amount &&
           this.currency.equals(other.currency);
  }

  static zero(currency: Currency): Money {
    return new Money(0, currency);
  }
}

class Address {
  constructor(
    public readonly street: string,
    public readonly city: string,
    public readonly state: string,
    public readonly zipCode: string,
    public readonly country: string
  ) {
    // Validate on construction
    if (!street || !city || !zipCode) {
      throw new Error('Invalid address');
    }
  }

  equals(other: Address): boolean {
    return this.street === other.street &&
           this.city === other.city &&
           this.state === other.state &&
           this.zipCode === other.zipCode &&
           this.country === other.country;
  }

  // Value objects are immutable - return new instance
  withStreet(street: string): Address {
    return new Address(street, this.city, this.state, this.zipCode, this.country);
  }
}

class DateRange {
  constructor(
    public readonly start: Date,
    public readonly end: Date
  ) {
    if (start > end) {
      throw new Error('Start date must be before end date');
    }
  }

  contains(date: Date): boolean {
    return date >= this.start && date <= this.end;
  }

  overlaps(other: DateRange): boolean {
    return this.start <= other.end && this.end >= other.start;
  }

  get durationInDays(): number {
    return Math.ceil((this.end.getTime() - this.start.getTime()) / (1000 * 60 * 60 * 24));
  }
}

// Typed ID as value object
class OrderId {
  constructor(public readonly value: string) {
    if (!value || value.length === 0) {
      throw new Error('OrderId cannot be empty');
    }
  }

  equals(other: OrderId): boolean {
    return this.value === other.value;
  }

  toString(): string {
    return this.value;
  }
}
```

**Value object characteristics:**
- Immutable (all properties readonly)
- No identity
- Equality based on all attributes
- Self-validating (validate in constructor)
- Side-effect free methods (return new instances)
- Can contain other value objects

**When to use value objects:**
- Representing concepts with no identity (money, addresses, dates)
- Typed IDs (OrderId, CustomerId)
- Measurements and quantities
- Any concept where equality means "same values"

### Aggregate

A cluster of entities and value objects with a defined boundary, treated as a single unit. One entity is the aggregate root.

```typescript
// Order is the Aggregate Root
class Order {
  private _id: OrderId;
  private _customerId: CustomerId;
  private _lineItems: LineItem[] = [];
  private _status: OrderStatus;
  private _shippingAddress: Address;

  constructor(id: OrderId, customerId: CustomerId, shippingAddress: Address) {
    this._id = id;
    this._customerId = customerId;
    this._shippingAddress = shippingAddress;
    this._status = OrderStatus.Draft;
  }

  get id(): OrderId { return this._id; }
  get customerId(): CustomerId { return this._customerId; }
  get status(): OrderStatus { return this._status; }
  get shippingAddress(): Address { return this._shippingAddress; }

  // Return copy to prevent external modification
  get lineItems(): ReadonlyArray<LineItem> { return [...this._lineItems]; }

  get total(): Money {
    return this._lineItems.reduce(
      (sum, item) => sum.add(item.subtotal),
      Money.zero(Currency.USD)
    );
  }

  // All modifications go through the aggregate root
  addLineItem(productId: ProductId, quantity: number, unitPrice: Money): void {
    this.ensureDraft();
    const existing = this._lineItems.find(li => li.productId.equals(productId));
    if (existing) {
      existing.increaseQuantity(quantity);
    } else {
      this._lineItems.push(new LineItem(productId, quantity, unitPrice));
    }
  }

  removeLineItem(productId: ProductId): void {
    this.ensureDraft();
    const index = this._lineItems.findIndex(li => li.productId.equals(productId));
    if (index === -1) {
      throw new Error('Line item not found');
    }
    this._lineItems.splice(index, 1);
  }

  updateShippingAddress(address: Address): void {
    this.ensureDraft();
    this._shippingAddress = address;
  }

  submit(): void {
    this.ensureDraft();
    if (this._lineItems.length === 0) {
      throw new Error('Cannot submit empty order');
    }
    this._status = OrderStatus.Submitted;
  }

  cancel(): void {
    if (this._status === OrderStatus.Shipped) {
      throw new Error('Cannot cancel shipped order');
    }
    this._status = OrderStatus.Cancelled;
  }

  private ensureDraft(): void {
    if (this._status !== OrderStatus.Draft) {
      throw new Error('Order is not in draft status');
    }
  }
}

// LineItem is an entity within the Order aggregate
// It has local identity (within the order) but not global identity
class LineItem {
  constructor(
    public readonly productId: ProductId,
    private _quantity: number,
    public readonly unitPrice: Money
  ) {
    if (_quantity <= 0) {
      throw new Error('Quantity must be positive');
    }
  }

  get quantity(): number { return this._quantity; }
  get subtotal(): Money { return this.unitPrice.multiply(this._quantity); }

  increaseQuantity(amount: number): void {
    if (amount <= 0) {
      throw new Error('Amount must be positive');
    }
    this._quantity += amount;
  }

  decreaseQuantity(amount: number): void {
    if (amount <= 0 || amount > this._quantity) {
      throw new Error('Invalid amount');
    }
    this._quantity -= amount;
  }
}
```

**Aggregate rules:**
1. **Root entity only**: External objects can only reference the aggregate root
2. **Root controls access**: All changes to internal objects go through the root
3. **Transactional boundary**: Aggregates are loaded and saved as a whole
4. **Keep small**: Large aggregates cause concurrency and performance issues
5. **Reference by ID**: Reference other aggregates by ID, not direct reference
6. **Invariant enforcement**: Root ensures all invariants are satisfied

**Aggregate design guidelines:**
```typescript
// BAD: Large aggregate with too many responsibilities
class Customer {
  orders: Order[];           // Should be separate aggregate
  invoices: Invoice[];       // Should be separate aggregate
  supportTickets: Ticket[];  // Should be separate aggregate
}

// GOOD: Small, focused aggregates referencing by ID
class Customer {
  id: CustomerId;
  name: CustomerName;
  email: Email;
  // Orders, invoices, tickets are separate aggregates
  // that reference customerId
}

class Order {
  id: OrderId;
  customerId: CustomerId;  // Reference by ID, not Customer object
  lineItems: LineItem[];
}
```

### Repository

Provides collection-like interface for accessing aggregates, abstracting persistence.

```typescript
// Repository interface (in domain layer)
interface OrderRepository {
  nextId(): OrderId;
  findById(id: OrderId): Promise<Order | null>;
  findByCustomerId(customerId: CustomerId): Promise<Order[]>;
  findPendingOrders(): Promise<Order[]>;
  save(order: Order): Promise<void>;
  delete(order: Order): Promise<void>;
}

// Repository implementation (in infrastructure layer)
class PostgresOrderRepository implements OrderRepository {
  constructor(private db: Database) {}

  nextId(): OrderId {
    return new OrderId(uuid());
  }

  async findById(id: OrderId): Promise<Order | null> {
    const row = await this.db.query(
      'SELECT * FROM orders WHERE id = $1',
      [id.value]
    );
    if (!row) return null;
    return this.toDomain(row);
  }

  async findByCustomerId(customerId: CustomerId): Promise<Order[]> {
    const rows = await this.db.query(
      'SELECT * FROM orders WHERE customer_id = $1',
      [customerId.value]
    );
    return Promise.all(rows.map(row => this.toDomain(row)));
  }

  async findPendingOrders(): Promise<Order[]> {
    const rows = await this.db.query(
      "SELECT * FROM orders WHERE status = 'pending'"
    );
    return Promise.all(rows.map(row => this.toDomain(row)));
  }

  async save(order: Order): Promise<void> {
    await this.db.transaction(async (tx) => {
      // Upsert order
      await tx.query(
        `INSERT INTO orders (id, customer_id, status, shipping_address, created_at)
         VALUES ($1, $2, $3, $4, $5)
         ON CONFLICT (id) DO UPDATE SET
           status = EXCLUDED.status,
           shipping_address = EXCLUDED.shipping_address`,
        [
          order.id.value,
          order.customerId.value,
          order.status,
          JSON.stringify(order.shippingAddress),
          order.createdAt
        ]
      );

      // Replace line items
      await tx.query('DELETE FROM line_items WHERE order_id = $1', [order.id.value]);

      for (const item of order.lineItems) {
        await tx.query(
          `INSERT INTO line_items (order_id, product_id, quantity, unit_price, currency)
           VALUES ($1, $2, $3, $4, $5)`,
          [
            order.id.value,
            item.productId.value,
            item.quantity,
            item.unitPrice.amount,
            item.unitPrice.currency.code
          ]
        );
      }
    });
  }

  async delete(order: Order): Promise<void> {
    await this.db.transaction(async (tx) => {
      await tx.query('DELETE FROM line_items WHERE order_id = $1', [order.id.value]);
      await tx.query('DELETE FROM orders WHERE id = $1', [order.id.value]);
    });
  }

  private async toDomain(row: any): Promise<Order> {
    const lineItemRows = await this.db.query(
      'SELECT * FROM line_items WHERE order_id = $1',
      [row.id]
    );

    // Use factory or reconstitution method
    return OrderFactory.reconstitute({
      id: row.id,
      customerId: row.customer_id,
      status: row.status,
      shippingAddress: JSON.parse(row.shipping_address),
      lineItems: lineItemRows.map(li => ({
        productId: li.product_id,
        quantity: li.quantity,
        unitPrice: { amount: li.unit_price, currency: li.currency }
      })),
      createdAt: row.created_at
    });
  }
}
```

**Repository characteristics:**
- One repository per aggregate type
- Provides illusion of in-memory collection
- Encapsulates query logic
- Returns fully reconstituted aggregates
- Interface in domain layer, implementation in infrastructure

### Domain Service

Contains domain logic that doesn't naturally fit within an entity or value object.

```typescript
// Logic that spans multiple aggregates
class OrderPricingService {
  constructor(
    private discountPolicy: DiscountPolicy,
    private taxCalculator: TaxCalculator
  ) {}

  calculateTotal(order: Order, customer: Customer): OrderTotal {
    const subtotal = order.lineItems.reduce(
      (sum, item) => sum.add(item.subtotal),
      Money.zero(Currency.USD)
    );

    const discount = this.discountPolicy.calculateDiscount(order, customer);
    const afterDiscount = subtotal.subtract(discount);

    const tax = this.taxCalculator.calculate(afterDiscount, order.shippingAddress);

    return new OrderTotal(subtotal, discount, tax, afterDiscount.add(tax));
  }
}

// Logic that requires external information
class InventoryAllocationService {
  constructor(private inventoryRepository: InventoryRepository) {}

  async allocateInventory(order: Order): Promise<AllocationResult> {
    const allocations: Allocation[] = [];

    for (const lineItem of order.lineItems) {
      const inventory = await this.inventoryRepository.findByProductId(lineItem.productId);

      if (!inventory || inventory.availableQuantity < lineItem.quantity) {
        return AllocationResult.insufficientInventory(lineItem.productId);
      }

      inventory.allocate(lineItem.quantity, order.id);
      allocations.push(new Allocation(lineItem.productId, lineItem.quantity));
    }

    return AllocationResult.success(allocations);
  }
}

// Transfer between aggregates
class FundsTransferService {
  async transfer(
    fromAccount: Account,
    toAccount: Account,
    amount: Money
  ): Promise<TransferResult> {
    if (!fromAccount.canWithdraw(amount)) {
      return TransferResult.insufficientFunds();
    }

    fromAccount.withdraw(amount);
    toAccount.deposit(amount);

    return TransferResult.success();
  }
}
```

**When to use domain services:**
- Operation involves multiple aggregates
- Operation requires external information
- Logic doesn't belong to any single entity
- Stateless operations on domain objects
- Complex calculations or validations

**Domain service vs Application service:**
```typescript
// Domain Service - pure domain logic
class OrderPricingService {
  calculateTotal(order: Order, customer: Customer): OrderTotal {
    // Domain logic only
  }
}

// Application Service - orchestration, transactions, infrastructure
class SubmitOrderUseCase {
  async execute(orderId: string): Promise<SubmitOrderResult> {
    // Load aggregates
    // Call domain services
    // Save changes
    // Dispatch events
  }
}
```

### Domain Event

Records something significant that happened in the domain.

```typescript
interface DomainEvent {
  occurredOn: Date;
  aggregateId: string;
  aggregateType: string;
}

class OrderSubmitted implements DomainEvent {
  public readonly occurredOn: Date;
  public readonly aggregateType = 'Order';

  constructor(
    public readonly aggregateId: string,
    public readonly customerId: string,
    public readonly orderTotal: number,
    public readonly lineItemCount: number
  ) {
    this.occurredOn = new Date();
  }
}

class OrderShipped implements DomainEvent {
  public readonly occurredOn: Date;
  public readonly aggregateType = 'Order';

  constructor(
    public readonly aggregateId: string,
    public readonly trackingNumber: string,
    public readonly carrier: string,
    public readonly estimatedDelivery: Date
  ) {
    this.occurredOn = new Date();
  }
}

class PaymentReceived implements DomainEvent {
  public readonly occurredOn: Date;
  public readonly aggregateType = 'Order';

  constructor(
    public readonly aggregateId: string,
    public readonly paymentId: string,
    public readonly amount: number,
    public readonly currency: string
  ) {
    this.occurredOn = new Date();
  }
}

// Aggregate collects domain events
class Order {
  private _domainEvents: DomainEvent[] = [];

  get domainEvents(): ReadonlyArray<DomainEvent> {
    return [...this._domainEvents];
  }

  clearDomainEvents(): void {
    this._domainEvents = [];
  }

  protected addDomainEvent(event: DomainEvent): void {
    this._domainEvents.push(event);
  }

  submit(): void {
    // ... validation logic ...
    this._status = OrderStatus.Submitted;
    this.addDomainEvent(new OrderSubmitted(
      this._id.value,
      this._customerId.value,
      this.total.amount,
      this._lineItems.length
    ));
  }

  ship(trackingNumber: string, carrier: string, estimatedDelivery: Date): void {
    // ... validation logic ...
    this._status = OrderStatus.Shipped;
    this.addDomainEvent(new OrderShipped(
      this._id.value,
      trackingNumber,
      carrier,
      estimatedDelivery
    ));
  }
}

// Event dispatcher
class DomainEventDispatcher {
  private handlers: Map<string, ((event: DomainEvent) => Promise<void>)[]> = new Map();

  register<T extends DomainEvent>(
    eventType: new (...args: any[]) => T,
    handler: (event: T) => Promise<void>
  ): void {
    const typeName = eventType.name;
    if (!this.handlers.has(typeName)) {
      this.handlers.set(typeName, []);
    }
    this.handlers.get(typeName)!.push(handler as any);
  }

  async dispatch(event: DomainEvent): Promise<void> {
    const handlers = this.handlers.get(event.constructor.name) || [];
    await Promise.all(handlers.map(handler => handler(event)));
  }

  async dispatchAll(events: DomainEvent[]): Promise<void> {
    for (const event of events) {
      await this.dispatch(event);
    }
  }
}

// Usage - register handlers
dispatcher.register(OrderSubmitted, async (event) => {
  await emailService.sendOrderConfirmation(event.aggregateId);
});

dispatcher.register(OrderSubmitted, async (event) => {
  await analyticsService.trackOrderSubmission(event);
});

dispatcher.register(OrderShipped, async (event) => {
  await notificationService.sendShippingNotification(event);
});
```

**Domain event characteristics:**
- Immutable
- Named in past tense (OrderSubmitted, not SubmitOrder)
- Contains all relevant data at time of occurrence
- Enables loose coupling between aggregates
- Supports eventual consistency
- Can be persisted for audit trail / event sourcing

### Factory

Encapsulates complex object creation logic.

```typescript
class OrderFactory {
  constructor(
    private orderRepository: OrderRepository,
    private productRepository: ProductRepository,
    private pricingService: PricingService
  ) {}

  // Complex creation from shopping cart
  async createFromCart(cart: ShoppingCart, customer: Customer): Promise<Order> {
    const orderId = this.orderRepository.nextId();
    const order = new Order(orderId, customer.id, customer.defaultShippingAddress);

    for (const cartItem of cart.items) {
      const product = await this.productRepository.findById(cartItem.productId);
      if (!product) {
        throw new Error(`Product not found: ${cartItem.productId}`);
      }

      const price = await this.pricingService.getPriceForCustomer(product, customer);
      order.addLineItem(product.id, cartItem.quantity, price);
    }

    return order;
  }

  // Reconstitution from persistence (no validation)
  static reconstitute(data: OrderData): Order {
    return new Order(
      new OrderId(data.id),
      new CustomerId(data.customerId),
      Address.fromData(data.shippingAddress),
      data.lineItems.map(li => LineItem.fromData(li)),
      OrderStatus.fromString(data.status),
      data.createdAt
    );
  }
}

// Factory method on aggregate for simple cases
class Order {
  static create(customerId: CustomerId, shippingAddress: Address): Order {
    return new Order(
      OrderId.generate(),
      customerId,
      shippingAddress
    );
  }
}
```

**When to use factories:**
- Creation involves multiple steps
- Creation requires fetching related data
- Different creation strategies exist
- Separating creation from reconstitution

### Specification

Encapsulates business rules for querying and validation.

```typescript
interface Specification<T> {
  isSatisfiedBy(candidate: T): boolean;
  and(other: Specification<T>): Specification<T>;
  or(other: Specification<T>): Specification<T>;
  not(): Specification<T>;
}

abstract class CompositeSpecification<T> implements Specification<T> {
  abstract isSatisfiedBy(candidate: T): boolean;

  and(other: Specification<T>): Specification<T> {
    return new AndSpecification(this, other);
  }

  or(other: Specification<T>): Specification<T> {
    return new OrSpecification(this, other);
  }

  not(): Specification<T> {
    return new NotSpecification(this);
  }
}

class AndSpecification<T> extends CompositeSpecification<T> {
  constructor(
    private left: Specification<T>,
    private right: Specification<T>
  ) {
    super();
  }

  isSatisfiedBy(candidate: T): boolean {
    return this.left.isSatisfiedBy(candidate) &&
           this.right.isSatisfiedBy(candidate);
  }
}

class OrSpecification<T> extends CompositeSpecification<T> {
  constructor(
    private left: Specification<T>,
    private right: Specification<T>
  ) {
    super();
  }

  isSatisfiedBy(candidate: T): boolean {
    return this.left.isSatisfiedBy(candidate) ||
           this.right.isSatisfiedBy(candidate);
  }
}

class NotSpecification<T> extends CompositeSpecification<T> {
  constructor(private spec: Specification<T>) {
    super();
  }

  isSatisfiedBy(candidate: T): boolean {
    return !this.spec.isSatisfiedBy(candidate);
  }
}

// Domain-specific specifications
class OrderReadyForShipment extends CompositeSpecification<Order> {
  isSatisfiedBy(order: Order): boolean {
    return order.status === OrderStatus.Paid &&
           order.hasShippingAddress &&
           order.lineItems.length > 0;
  }
}

class HighValueOrder extends CompositeSpecification<Order> {
  constructor(private threshold: Money) {
    super();
  }

  isSatisfiedBy(order: Order): boolean {
    return order.total.isGreaterThan(this.threshold);
  }
}

class CustomerEligibleForDiscount extends CompositeSpecification<Customer> {
  isSatisfiedBy(customer: Customer): boolean {
    return customer.membershipLevel === MembershipLevel.Gold ||
           customer.totalPurchases.isGreaterThan(Money.of(1000, Currency.USD));
  }
}

class RecentOrder extends CompositeSpecification<Order> {
  constructor(private days: number) {
    super();
  }

  isSatisfiedBy(order: Order): boolean {
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - this.days);
    return order.createdAt >= cutoff;
  }
}

// Usage - compose specifications
const readyForShipment = new OrderReadyForShipment();
const highValue = new HighValueOrder(Money.of(500, Currency.USD));
const recent = new RecentOrder(30);

// Find priority orders: ready for shipment AND (high value OR recent)
const prioritySpec = readyForShipment.and(highValue.or(recent));

const priorityOrders = orders.filter(order => prioritySpec.isSatisfiedBy(order));

// Use for validation
class OrderValidator {
  private readySpec = new OrderReadyForShipment();

  canShip(order: Order): boolean {
    return this.readySpec.isSatisfiedBy(order);
  }
}
```

**When to use specifications:**
- Reusable business rules
- Complex query criteria
- Validation logic
- Composable conditions

---

## DDD Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│              (Controllers, Views, DTOs)                      │
├─────────────────────────────────────────────────────────────┤
│                    Application Layer                         │
│         (Use Cases, Application Services, Commands)          │
├─────────────────────────────────────────────────────────────┤
│                      Domain Layer                            │
│  (Entities, Value Objects, Aggregates, Domain Services,      │
│   Repository Interfaces, Domain Events, Specifications)      │
├─────────────────────────────────────────────────────────────┤
│                   Infrastructure Layer                       │
│    (Repository Implementations, External Services,           │
│     Persistence, Messaging, Framework Integration)           │
└─────────────────────────────────────────────────────────────┘
```

**Dependency rule:** Dependencies point inward. Domain layer has no dependencies on other layers.

```typescript
// Application Layer - orchestrates domain objects
class SubmitOrderUseCase {
  constructor(
    private orderRepository: OrderRepository,
    private inventoryService: InventoryAllocationService,
    private eventDispatcher: DomainEventDispatcher
  ) {}

  async execute(orderId: string): Promise<SubmitOrderResult> {
    // 1. Load aggregate
    const order = await this.orderRepository.findById(new OrderId(orderId));
    if (!order) {
      return SubmitOrderResult.orderNotFound();
    }

    // 2. Execute domain logic
    const allocation = await this.inventoryService.allocateInventory(order);
    if (!allocation.success) {
      return SubmitOrderResult.insufficientInventory(allocation.failedProduct);
    }

    order.submit();

    // 3. Persist changes
    await this.orderRepository.save(order);

    // 4. Dispatch domain events
    for (const event of order.domainEvents) {
      await this.eventDispatcher.dispatch(event);
    }
    order.clearDomainEvents();

    return SubmitOrderResult.success(order.id);
  }
}

// Command object (optional, for CQRS)
class SubmitOrderCommand {
  constructor(public readonly orderId: string) {}
}

class SubmitOrderHandler {
  constructor(private useCase: SubmitOrderUseCase) {}

  async handle(command: SubmitOrderCommand): Promise<SubmitOrderResult> {
    return this.useCase.execute(command.orderId);
  }
}
```

---

## Pattern Selection Guide

| Problem | Consider Pattern |
|---------|------------------|
| Complex domain logic | DDD Tactical Patterns |
| Large system with multiple teams | Bounded Contexts |
| Identity matters over time | Entity |
| Immutable descriptive object | Value Object |
| Cluster of related objects | Aggregate |
| Persistence abstraction | Repository |
| Cross-aggregate operations | Domain Service |
| React to domain changes | Domain Event |
| Reusable business rules | Specification |
| Complex object creation | Factory |
| Integrating external systems | Anti-Corruption Layer |
| Shared vocabulary with domain experts | Ubiquitous Language |
