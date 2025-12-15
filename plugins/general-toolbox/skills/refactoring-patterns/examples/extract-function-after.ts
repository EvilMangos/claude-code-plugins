/**
 * Example: Extract Function Refactoring - AFTER
 *
 * This file shows code AFTER applying the Extract Function refactoring.
 * Each responsibility is now in its own clearly-named function:
 * - printBanner() - prints the header
 * - calculateOutstanding() - computes total from orders
 * - printDetails() - shows invoice info
 * - calculateLateFee() - computes late penalties
 * - printLateFeeWarning() - shows late payment info
 *
 * Benefits:
 * - Each function does one thing
 * - Function names explain what they do
 * - Easier to test individual pieces
 * - Main function is now a high-level overview
 */

interface Order {
  amount: number;
}

interface Invoice {
  customer: string;
  orders: Order[];
  dueDate: Date;
}

function printBanner(): void {
  console.log("**********************************");
  console.log("******* Customer Invoice *********");
  console.log("**********************************");
}

function calculateOutstanding(orders: Order[]): number {
  return orders.reduce((sum, order) => sum + order.amount, 0);
}

function printDetails(invoice: Invoice, outstanding: number): void {
  console.log(`Customer: ${invoice.customer}`);
  console.log(`Amount: $${outstanding.toFixed(2)}`);
  console.log(`Due: ${invoice.dueDate.toLocaleDateString()}`);
}

function calculateDaysLate(dueDate: Date): number {
  const today = new Date();
  if (dueDate >= today) return 0;
  return Math.floor(
    (today.getTime() - dueDate.getTime()) / (1000 * 60 * 60 * 24)
  );
}

function calculateLateFee(outstanding: number, daysLate: number): number {
  if (daysLate <= 0) return 0;
  const monthsLate = Math.ceil(daysLate / 30);
  return outstanding * 0.05 * monthsLate;
}

function printLateFeeWarning(
  outstanding: number,
  daysLate: number,
  lateFee: number
): void {
  console.log(`WARNING: Payment is ${daysLate} days late!`);
  console.log(`Late fee: $${lateFee.toFixed(2)}`);
  console.log(`Total due: $${(outstanding + lateFee).toFixed(2)}`);
}

function printInvoice(invoice: Invoice): void {
  printBanner();

  const outstanding = calculateOutstanding(invoice.orders);
  printDetails(invoice, outstanding);

  const daysLate = calculateDaysLate(invoice.dueDate);
  if (daysLate > 0) {
    const lateFee = calculateLateFee(outstanding, daysLate);
    printLateFeeWarning(outstanding, daysLate, lateFee);
  }
}

// Usage
const invoice: Invoice = {
  customer: "Acme Corp",
  orders: [{ amount: 100 }, { amount: 250 }, { amount: 75 }],
  dueDate: new Date("2024-01-15"),
};

printInvoice(invoice);
