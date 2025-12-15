/**
 * Example: Replace Conditional with Polymorphism - BEFORE
 *
 * This file shows code BEFORE applying the refactoring.
 * Problems with this approach:
 * - Switch statement will grow with each new employee type
 * - Adding new type requires modifying existing code (violates OCP)
 * - Multiple switch statements likely exist for other behaviors
 * - Logic for each type is scattered across switch cases
 *
 * See replace-conditional-polymorphism-after.ts for the refactored version.
 */

type EmployeeType = "engineer" | "salesperson" | "manager";

interface Employee {
  type: EmployeeType;
  name: string;
  baseSalary: number;
  salesAmount?: number;
  teamSize?: number;
  overtimeHours?: number;
}

function calculatePay(employee: Employee): number {
  switch (employee.type) {
    case "engineer":
      // Engineers get base salary + overtime
      const overtimePay = (employee.overtimeHours ?? 0) * 50;
      return employee.baseSalary + overtimePay;

    case "salesperson":
      // Salespeople get base salary + 10% commission
      const commission = (employee.salesAmount ?? 0) * 0.1;
      return employee.baseSalary + commission;

    case "manager":
      // Managers get base salary + bonus per team member
      const teamBonus = (employee.teamSize ?? 0) * 500;
      return employee.baseSalary + teamBonus;

    default:
      throw new Error(`Unknown employee type: ${employee.type}`);
  }
}

function getDescription(employee: Employee): string {
  switch (employee.type) {
    case "engineer":
      return `${employee.name} is an engineer with ${employee.overtimeHours ?? 0} overtime hours`;

    case "salesperson":
      return `${employee.name} is a salesperson with $${employee.salesAmount ?? 0} in sales`;

    case "manager":
      return `${employee.name} is a manager leading ${employee.teamSize ?? 0} people`;

    default:
      throw new Error(`Unknown employee type: ${employee.type}`);
  }
}

// Usage
const employees: Employee[] = [
  { type: "engineer", name: "Alice", baseSalary: 5000, overtimeHours: 10 },
  { type: "salesperson", name: "Bob", baseSalary: 3000, salesAmount: 50000 },
  { type: "manager", name: "Carol", baseSalary: 6000, teamSize: 5 },
];

for (const emp of employees) {
  console.log(getDescription(emp));
  console.log(`Pay: $${calculatePay(emp)}`);
  console.log("---");
}
