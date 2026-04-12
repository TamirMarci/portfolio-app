
# Implement holdings derived from transactions

## TL;DR
Replace manually stored holdings with holdings derived from transactions.

## Type
Core Feature

## Priority
High

## Effort
Large

## Current behavior
- Holdings are stored directly in the database
- Transactions do not determine the final position

## Expected behavior
- Holdings are recalculated from transactions
- Transactions become the source of truth

## Calculation rules

quantity = SUM(BUY qty) − SUM(SELL qty)

If quantity > 0  
→ holding exists

If quantity <= 0  
→ holding removed from active holdings

## Requirements
Implement a recalculation engine:

recalculate_holding(asset_id)

Trigger this when:

- create transaction
- edit transaction
- delete transaction
- import transactions

## Acceptance criteria
- Adding BUY updates holdings
- Adding SELL updates holdings
- Editing transaction updates holdings
- Deleting transaction updates holdings
