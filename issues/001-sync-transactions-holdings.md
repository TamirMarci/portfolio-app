# Sync Holdings with Transactions

## TL;DR
Transactions are the source of truth for portfolio positions.

Whenever a transaction is created, updated, deleted, or imported, the corresponding holding must be recalculated automatically so that holdings always reflect the aggregated transaction history.

---

## Type
Feature

## Priority
Normal

## Effort
Medium

---

# Current Behavior

- Holdings are imported directly from Excel and stored as static records.
- Transactions are imported separately.
- Adding or modifying transactions does **not update holdings**.
- Holdings can therefore become inconsistent with the actual transaction history.

---

# Desired Architecture

Transactions become the **source of truth**.

Holdings become **derived state** calculated from transactions.

Workflow:

Create / Update / Delete Transaction  
→ Persist transaction in DB  
→ Recalculate holding for that symbol  
→ Update portfolio totals

---

# Expected Behavior

When a transaction is created:

1. The transaction is saved in the database.
2. The system identifies the transaction symbol (e.g. AAPL).
3. All transactions for that symbol are aggregated.
4. The corresponding holding is recalculated.

If the holding does not exist → create it.

If the aggregated quantity becomes zero → remove or mark the holding as inactive.

Holdings must always represent the current position derived from all transactions.

---

# Holding Calculation Rules

For each symbol:

Quantity:

quantity = SUM(buy_quantity) − SUM(sell_quantity)

Average Price:

avg_price = weighted average of BUY transactions

Notes:

- SELL transactions decrease quantity.
- SELL transactions do not change the average price of remaining shares.
- If quantity becomes zero → remove or deactivate the holding.

---

# Events That Must Trigger Recalculation

Holding recalculation should occur when:

- A transaction is **created**
- A transaction is **updated**
- A transaction is **deleted**
- Transactions are **imported from Excel**

Recalculation should only affect the holding for the relevant symbol.

---

# Relevant Files

backend/app/services/portfolio_service.py  
backend/app/repositories/holding_repo.py  
backend/app/repositories/transaction_repo.py  

Potential additional files:

transaction_service.py (if exists)  
Excel import pipeline

---

# Risks / Dependencies

- The existing pipeline imports holdings directly from Excel.
- Migration may be required to compute holdings from transactions instead.
- Performance considerations when aggregating large transaction histories.
- Ensure recalculation affects only the relevant symbol.

---

# Acceptance Criteria

- Creating a transaction stores it in the database.
- Creating a transaction immediately updates the corresponding holding.
- Updating a transaction recalculates the holding.
- Deleting a transaction recalculates the holding.
- Importing transactions from Excel updates holdings.
- Holdings quantity equals aggregated BUY − SELL transactions.
- Average price is calculated correctly.
- Holdings with zero quantity are removed or marked inactive.
- Portfolio totals remain correct after updates.
- No duplicate holdings exist for the same symbol.
- Running imports multiple times produces consistent results (idempotent).