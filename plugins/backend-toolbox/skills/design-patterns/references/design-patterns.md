# Design Patterns - Comprehensive Reference

This reference covers creational, structural, and behavioral design patterns, with selection guidance for common problems.

## Creational Patterns

### Factory Method

**Intent:** Define an interface for creating objects, but let subclasses decide which class to instantiate.

**When to use:**

- Object creation logic is complex
- Creation varies based on conditions
- Need to decouple creation from usage

```typescript
// Abstract factory method
interface PaymentProcessor {
  process(amount: number): void;
}

abstract class PaymentProcessorFactory {
  abstract createProcessor(): PaymentProcessor;

  processPayment(amount: number): void {
    const processor = this.createProcessor();
    processor.process(amount);
  }
}

// Concrete factories
class StripeProcessorFactory extends PaymentProcessorFactory {
  createProcessor(): PaymentProcessor {
    return new StripeProcessor();
  }
}

class PayPalProcessorFactory extends PaymentProcessorFactory {
  createProcessor(): PaymentProcessor {
    return new PayPalProcessor();
  }
}
```

### Abstract Factory

**Intent:** Create families of related objects without specifying concrete classes.

**When to use:**

- System should be independent of how products are created
- Need to enforce that products from the same family are used together
- Multiple product variations exist

```typescript
interface UIFactory {
  createButton(): Button;
  createCheckbox(): Checkbox;
  createTextField(): TextField;
}

class MaterialUIFactory implements UIFactory {
  createButton(): Button {
    return new MaterialButton();
  }
  createCheckbox(): Checkbox {
    return new MaterialCheckbox();
  }
  createTextField(): TextField {
    return new MaterialTextField();
  }
}

class BootstrapUIFactory implements UIFactory {
  createButton(): Button {
    return new BootstrapButton();
  }
  createCheckbox(): Checkbox {
    return new BootstrapCheckbox();
  }
  createTextField(): TextField {
    return new BootstrapTextField();
  }
}
```

### Builder

**Intent:** Construct complex objects step by step, allowing different representations.

**When to use:**

- Object has many optional parameters
- Construction involves multiple steps
- Want to prevent incomplete object creation

```typescript
class QueryBuilder {
  private query: Query = new Query();

  select(...columns: string[]): this {
    this.query.columns = columns;
    return this;
  }

  from(table: string): this {
    this.query.table = table;
    return this;
  }

  where(condition: string): this {
    this.query.conditions.push(condition);
    return this;
  }

  orderBy(column: string, direction: "ASC" | "DESC" = "ASC"): this {
    this.query.orderBy = { column, direction };
    return this;
  }

  limit(n: number): this {
    this.query.limit = n;
    return this;
  }

  build(): Query {
    if (!this.query.table) throw new Error("Table is required");
    return this.query;
  }
}

// Usage
const query = new QueryBuilder()
  .select("id", "name", "email")
  .from("users")
  .where("active = true")
  .orderBy("created_at", "DESC")
  .limit(10)
  .build();
```

### Singleton

**Intent:** Ensure a class has only one instance with global access point.

**When to use:**

- Exactly one instance is needed (configuration, connection pool)
- Controlled access to sole instance required

**Caution:** Often overused. Consider dependency injection instead.

```typescript
class Configuration {
  private static instance: Configuration;
  private settings: Map<string, string> = new Map();

  private constructor() {
    // Private constructor prevents direct instantiation
  }

  static getInstance(): Configuration {
    if (!Configuration.instance) {
      Configuration.instance = new Configuration();
    }
    return Configuration.instance;
  }

  get(key: string): string | undefined {
    return this.settings.get(key);
  }

  set(key: string, value: string): void {
    this.settings.set(key, value);
  }
}

// Better alternative: dependency injection
class ConfigurationService {
  constructor(private settings: Map<string, string>) {}
  // ... same methods but injectable and testable
}
```

---

## Structural Patterns

### Adapter

**Intent:** Convert interface of a class into another interface clients expect.

**When to use:**

- Integrating with legacy code or third-party libraries
- Interface doesn't match what client expects
- Need to make incompatible classes work together

```typescript
// External library with incompatible interface
class LegacyPrinter {
  printDocument(doc: string, copies: number): void {
    console.log(`Printing ${copies} copies of: ${doc}`);
  }
}

// Interface our system expects
interface Printer {
  print(content: string): void;
}

// Adapter makes LegacyPrinter work with our interface
class LegacyPrinterAdapter implements Printer {
  constructor(private legacyPrinter: LegacyPrinter) {}

  print(content: string): void {
    this.legacyPrinter.printDocument(content, 1);
  }
}

// Usage
function printReport(printer: Printer, report: string): void {
  printer.print(report);
}

const adapter = new LegacyPrinterAdapter(new LegacyPrinter());
printReport(adapter, "Annual Report");
```

### Decorator

**Intent:** Attach additional responsibilities to objects dynamically.

**When to use:**

- Add responsibilities without modifying existing code
- Responsibilities can be combined in various ways
- Subclassing would create explosion of classes

```typescript
interface Coffee {
  cost(): number;
  description(): string;
}

class SimpleCoffee implements Coffee {
  cost(): number {
    return 2;
  }
  description(): string {
    return "Simple coffee";
  }
}

// Decorators
abstract class CoffeeDecorator implements Coffee {
  constructor(protected coffee: Coffee) {}
  abstract cost(): number;
  abstract description(): string;
}

class MilkDecorator extends CoffeeDecorator {
  cost(): number {
    return this.coffee.cost() + 0.5;
  }
  description(): string {
    return this.coffee.description() + ", milk";
  }
}

class SugarDecorator extends CoffeeDecorator {
  cost(): number {
    return this.coffee.cost() + 0.25;
  }
  description(): string {
    return this.coffee.description() + ", sugar";
  }
}

class WhipDecorator extends CoffeeDecorator {
  cost(): number {
    return this.coffee.cost() + 0.75;
  }
  description(): string {
    return this.coffee.description() + ", whip";
  }
}

// Usage - combine decorators
let coffee: Coffee = new SimpleCoffee();
coffee = new MilkDecorator(coffee);
coffee = new SugarDecorator(coffee);
coffee = new WhipDecorator(coffee);

console.log(coffee.description()); // Simple coffee, milk, sugar, whip
console.log(coffee.cost()); // 3.5
```

### Facade

**Intent:** Provide unified interface to a set of interfaces in a subsystem.

**When to use:**

- Simplify complex subsystem for common use cases
- Reduce coupling between clients and subsystem
- Layer subsystems

```typescript
// Complex subsystem classes
class VideoDecoder {
  decode(file: string): VideoData {
    /* ... */
  }
}

class AudioDecoder {
  decode(file: string): AudioData {
    /* ... */
  }
}

class VideoRenderer {
  render(video: VideoData, screen: Screen): void {
    /* ... */
  }
}

class AudioPlayer {
  play(audio: AudioData, speakers: Speakers): void {
    /* ... */
  }
}

class SubtitleLoader {
  load(file: string): Subtitles {
    /* ... */
  }
}

// Facade simplifies the complex subsystem
class VideoPlayerFacade {
  private videoDecoder = new VideoDecoder();
  private audioDecoder = new AudioDecoder();
  private videoRenderer = new VideoRenderer();
  private audioPlayer = new AudioPlayer();
  private subtitleLoader = new SubtitleLoader();

  play(
    videoFile: string,
    screen: Screen,
    speakers: Speakers,
    subtitleFile?: string
  ): void {
    const video = this.videoDecoder.decode(videoFile);
    const audio = this.audioDecoder.decode(videoFile);

    this.videoRenderer.render(video, screen);
    this.audioPlayer.play(audio, speakers);

    if (subtitleFile) {
      const subtitles = this.subtitleLoader.load(subtitleFile);
      screen.showSubtitles(subtitles);
    }
  }
}

// Simple usage
const player = new VideoPlayerFacade();
player.play("movie.mp4", screen, speakers, "movie.srt");
```

### Composite

**Intent:** Compose objects into tree structures to represent part-whole hierarchies.

**When to use:**

- Represent hierarchies of objects
- Clients should treat individual objects and compositions uniformly
- Tree-like structures

```typescript
interface FileSystemNode {
  getName(): string;
  getSize(): number;
  print(indent?: string): void;
}

class File implements FileSystemNode {
  constructor(private name: string, private size: number) {}

  getName(): string {
    return this.name;
  }
  getSize(): number {
    return this.size;
  }
  print(indent = ""): void {
    console.log(`${indent}${this.name} (${this.size}KB)`);
  }
}

class Directory implements FileSystemNode {
  private children: FileSystemNode[] = [];

  constructor(private name: string) {}

  add(node: FileSystemNode): void {
    this.children.push(node);
  }

  getName(): string {
    return this.name;
  }

  getSize(): number {
    return this.children.reduce((sum, child) => sum + child.getSize(), 0);
  }

  print(indent = ""): void {
    console.log(`${indent}${this.name}/`);
    this.children.forEach((child) => child.print(indent + "  "));
  }
}

// Usage
const root = new Directory("root");
const src = new Directory("src");
src.add(new File("index.ts", 10));
src.add(new File("app.ts", 25));
root.add(src);
root.add(new File("package.json", 2));

root.print();
console.log(`Total size: ${root.getSize()}KB`);
```

---

## Behavioral Patterns

### Strategy

**Intent:** Define family of algorithms, encapsulate each one, make them interchangeable.

**When to use:**

- Multiple algorithms for a task
- Algorithm selection at runtime
- Avoid conditional statements for algorithm selection

```typescript
interface SortStrategy {
  sort(data: number[]): number[];
}

class QuickSort implements SortStrategy {
  sort(data: number[]): number[] {
    // Quick sort implementation
    return [...data].sort((a, b) => a - b);
  }
}

class MergeSort implements SortStrategy {
  sort(data: number[]): number[] {
    // Merge sort implementation
    return [...data].sort((a, b) => a - b);
  }
}

class BubbleSort implements SortStrategy {
  sort(data: number[]): number[] {
    const arr = [...data];
    for (let i = 0; i < arr.length; i++) {
      for (let j = 0; j < arr.length - i - 1; j++) {
        if (arr[j] > arr[j + 1]) {
          [arr[j], arr[j + 1]] = [arr[j + 1], arr[j]];
        }
      }
    }
    return arr;
  }
}

class Sorter {
  constructor(private strategy: SortStrategy) {}

  setStrategy(strategy: SortStrategy): void {
    this.strategy = strategy;
  }

  sort(data: number[]): number[] {
    return this.strategy.sort(data);
  }
}

// Usage
const sorter = new Sorter(new QuickSort());
sorter.sort([3, 1, 4, 1, 5]);

sorter.setStrategy(new BubbleSort()); // Switch algorithm at runtime
sorter.sort([3, 1, 4, 1, 5]);
```

### Observer

**Intent:** Define one-to-many dependency so when one object changes state, dependents are notified.

**When to use:**

- Changes to one object require changing others
- Object should notify others without knowing who they are
- Event-driven systems

```typescript
interface Observer {
  update(event: string, data: any): void;
}

class EventEmitter {
  private observers: Map<string, Observer[]> = new Map();

  subscribe(event: string, observer: Observer): void {
    if (!this.observers.has(event)) {
      this.observers.set(event, []);
    }
    this.observers.get(event)!.push(observer);
  }

  unsubscribe(event: string, observer: Observer): void {
    const observers = this.observers.get(event);
    if (observers) {
      const index = observers.indexOf(observer);
      if (index > -1) observers.splice(index, 1);
    }
  }

  emit(event: string, data: any): void {
    const observers = this.observers.get(event);
    if (observers) {
      observers.forEach((observer) => observer.update(event, data));
    }
  }
}

// Usage
class OrderService extends EventEmitter {
  createOrder(order: Order): void {
    // Create order logic
    this.emit("orderCreated", order);
  }
}

class EmailNotifier implements Observer {
  update(event: string, data: Order): void {
    if (event === "orderCreated") {
      console.log(`Sending email for order ${data.id}`);
    }
  }
}

class InventoryUpdater implements Observer {
  update(event: string, data: Order): void {
    if (event === "orderCreated") {
      console.log(`Updating inventory for order ${data.id}`);
    }
  }
}

const orderService = new OrderService();
orderService.subscribe("orderCreated", new EmailNotifier());
orderService.subscribe("orderCreated", new InventoryUpdater());
```

### Command

**Intent:** Encapsulate a request as an object, allowing parameterization and queuing.

**When to use:**

- Parameterize objects with operations
- Queue, log, or support undo for operations
- Structure system around high-level operations

```typescript
interface Command {
  execute(): void;
  undo(): void;
}

class TextEditor {
  private content = "";

  getContent(): string {
    return this.content;
  }

  insert(text: string, position: number): void {
    this.content =
      this.content.slice(0, position) + text + this.content.slice(position);
  }

  delete(position: number, length: number): void {
    this.content =
      this.content.slice(0, position) + this.content.slice(position + length);
  }
}

class InsertCommand implements Command {
  constructor(
    private editor: TextEditor,
    private text: string,
    private position: number
  ) {}

  execute(): void {
    this.editor.insert(this.text, this.position);
  }

  undo(): void {
    this.editor.delete(this.position, this.text.length);
  }
}

class CommandHistory {
  private history: Command[] = [];
  private current = -1;

  execute(command: Command): void {
    // Remove any redo history
    this.history = this.history.slice(0, this.current + 1);
    command.execute();
    this.history.push(command);
    this.current++;
  }

  undo(): void {
    if (this.current >= 0) {
      this.history[this.current].undo();
      this.current--;
    }
  }

  redo(): void {
    if (this.current < this.history.length - 1) {
      this.current++;
      this.history[this.current].execute();
    }
  }
}
```

### State

**Intent:** Allow object to alter its behavior when internal state changes.

**When to use:**

- Object behavior depends on state
- Operations have large conditional statements based on state
- State transitions are explicit

```typescript
interface OrderState {
  proceed(order: Order): void;
  cancel(order: Order): void;
  getStatus(): string;
}

class PendingState implements OrderState {
  proceed(order: Order): void {
    order.setState(new ProcessingState());
  }
  cancel(order: Order): void {
    order.setState(new CancelledState());
  }
  getStatus(): string {
    return "PENDING";
  }
}

class ProcessingState implements OrderState {
  proceed(order: Order): void {
    order.setState(new ShippedState());
  }
  cancel(order: Order): void {
    throw new Error("Cannot cancel order in processing");
  }
  getStatus(): string {
    return "PROCESSING";
  }
}

class ShippedState implements OrderState {
  proceed(order: Order): void {
    order.setState(new DeliveredState());
  }
  cancel(order: Order): void {
    throw new Error("Cannot cancel shipped order");
  }
  getStatus(): string {
    return "SHIPPED";
  }
}

class DeliveredState implements OrderState {
  proceed(order: Order): void {
    throw new Error("Order already delivered");
  }
  cancel(order: Order): void {
    throw new Error("Cannot cancel delivered order");
  }
  getStatus(): string {
    return "DELIVERED";
  }
}

class CancelledState implements OrderState {
  proceed(order: Order): void {
    throw new Error("Cannot proceed cancelled order");
  }
  cancel(order: Order): void {
    throw new Error("Order already cancelled");
  }
  getStatus(): string {
    return "CANCELLED";
  }
}

class Order {
  private state: OrderState = new PendingState();

  setState(state: OrderState): void {
    this.state = state;
  }

  proceed(): void {
    this.state.proceed(this);
  }

  cancel(): void {
    this.state.cancel(this);
  }

  getStatus(): string {
    return this.state.getStatus();
  }
}
```

---

## Pattern Selection Guide

| Problem                            | Consider Pattern      |
| ---------------------------------- | --------------------- |
| Object creation is complex         | Factory, Builder      |
| Need single instance               | Singleton (prefer DI) |
| Incompatible interfaces            | Adapter               |
| Add responsibilities dynamically   | Decorator             |
| Simplify complex subsystem         | Facade                |
| Tree/hierarchy structures          | Composite             |
| Swappable algorithms               | Strategy              |
| Notify multiple objects of changes | Observer              |
| Undo/redo, queuing operations      | Command               |
| Behavior varies by state           | State                 |

For Domain-Driven Design patterns (Entity, Value Object, Aggregate, Repository, Domain Service, Domain Event, Specification, Bounded Context, Anti-Corruption Layer), see **`references/domain-driven-design.md`**.
