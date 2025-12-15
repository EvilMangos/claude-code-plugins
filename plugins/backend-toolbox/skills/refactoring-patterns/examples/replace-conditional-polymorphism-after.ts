/**
 * Example: Replace Conditional with Polymorphism - AFTER
 *
 * This file shows code AFTER applying the refactoring.
 * Benefits:
 * - Each employee type is its own class
 * - Adding new type = adding new class (no existing code modified)
 * - Type-specific logic is co-located in each class
 * - No switch statements to maintain
 * - TypeScript enforces implementation of required methods
 *
 * To add a new employee type (e.g., Contractor):
 * 1. Create new class implementing Employee
 * 2. Add case to createEmployee factory
 * That's it - no other code changes needed!
 */

interface Employee {
  name: string;
  calculatePay(): number;
  getDescription(): string;
}

class Engineer implements Employee {
  constructor(
    public name: string,
    private baseSalary: number,
    private overtimeHours: number
  ) {}

  calculatePay(): number {
    const overtimePay = this.overtimeHours * 50;
    return this.baseSalary + overtimePay;
  }

  getDescription(): string {
    return `${this.name} is an engineer with ${this.overtimeHours} overtime hours`;
  }
}

class Salesperson implements Employee {
  constructor(
    public name: string,
    private baseSalary: number,
    private salesAmount: number
  ) {}

  calculatePay(): number {
    const commission = this.salesAmount * 0.1;
    return this.baseSalary + commission;
  }

  getDescription(): string {
    return `${this.name} is a salesperson with $${this.salesAmount} in sales`;
  }
}

class Manager implements Employee {
  constructor(
    public name: string,
    private baseSalary: number,
    private teamSize: number
  ) {}

  calculatePay(): number {
    const teamBonus = this.teamSize * 500;
    return this.baseSalary + teamBonus;
  }

  getDescription(): string {
    return `${this.name} is a manager leading ${this.teamSize} people`;
  }
}

// Factory function - the ONLY place that knows about specific types
type EmployeeData =
  | { type: "engineer"; name: string; baseSalary: number; overtimeHours: number }
  | { type: "salesperson"; name: string; baseSalary: number; salesAmount: number }
  | { type: "manager"; name: string; baseSalary: number; teamSize: number };

function createEmployee(data: EmployeeData): Employee {
  switch (data.type) {
    case "engineer":
      return new Engineer(data.name, data.baseSalary, data.overtimeHours);
    case "salesperson":
      return new Salesperson(data.name, data.baseSalary, data.salesAmount);
    case "manager":
      return new Manager(data.name, data.baseSalary, data.teamSize);
  }
}

// Usage - polymorphism in action
const employeeData: EmployeeData[] = [
  { type: "engineer", name: "Alice", baseSalary: 5000, overtimeHours: 10 },
  { type: "salesperson", name: "Bob", baseSalary: 3000, salesAmount: 50000 },
  { type: "manager", name: "Carol", baseSalary: 6000, teamSize: 5 },
];

const employees = employeeData.map(createEmployee);

for (const emp of employees) {
  // No switch needed - polymorphism handles it
  console.log(emp.getDescription());
  console.log(`Pay: $${emp.calculatePay()}`);
  console.log("---");
}
