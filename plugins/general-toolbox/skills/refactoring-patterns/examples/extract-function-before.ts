/**
 * Example: Extract Function Refactoring - BEFORE
 *
 * This file shows code BEFORE applying the Extract Function refactoring.
 * The printInvoice function is doing too many things:
 * - Printing a banner
 * - Calculating outstanding amount
 * - Printing invoice details
 *
 * See extract-function-after.ts for the refactored version.
 */

interface Order {
  amount: number;
}

interface Invoice {
  customer: string;
  orders: Order[];
  dueDate: Date;
}

function printInvoice(invoice: Invoice): void {
  let outstanding = 0;

  // Print banner
  console.log("**********************************");
  console.log("******* Customer Invoice *********");
  console.log("**********************************");

  // Calculate outstanding amount
  for (const order of invoice.orders) {
    outstanding += order.amount;
  }

  // Print details
  console.log(`Customer: ${invoice.customer}`);
  console.log(`Amount: $${outstanding.toFixed(2)}`);
  console.log(`Due: ${invoice.dueDate.toLocaleDateString()}`);

  // Print late fee warning if applicable
  const today = new Date();
  if (invoice.dueDate < today) {
    const daysLate = Math.floor(
      (today.getTime() - invoice.dueDate.getTime()) / (1000 * 60 * 60 * 24)
    );
    const lateFee = outstanding * 0.05 * Math.ceil(daysLate / 30);
    console.log(`WARNING: Payment is ${daysLate} days late!`);
    console.log(`Late fee: $${lateFee.toFixed(2)}`);
    console.log(`Total due: $${(outstanding + lateFee).toFixed(2)}`);
  }
}

// Usage
const invoice: Invoice = {
  customer: "Acme Corp",
  orders: [{ amount: 100 }, { amount: 250 }, { amount: 75 }],
  dueDate: new Date("2024-01-15"),
};

printInvoice(invoice);
