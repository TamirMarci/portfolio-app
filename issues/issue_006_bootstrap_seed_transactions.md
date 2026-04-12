
# Bootstrap existing holdings into seeded transactions

## TL;DR
Convert existing holdings imported from Excel into "seeded" transactions so the system can transition to transactions-derived holdings.

## Type
Migration / Data

## Priority
High

## Effort
Medium

## Current behavior
- Holdings are imported directly from the Excel Holdings sheet
- Transactions only represent activity after import
- The system cannot reconstruct current holdings purely from transactions

## Expected behavior
- For each existing holding, create a synthetic BUY transaction
- These transactions represent the starting portfolio state
- They are marked as bootstrap/seed transactions

## Bootstrap transaction rules
For each holding:

symbol = holding.symbol  
quantity = holding.quantity  
price_per_share = holding.avg_cost  
trade_date = bootstrap_date  
is_bootstrap = true  
source = "excel_import"

Example:

BUY NVDA  
qty = 39  
price = 85.38  
is_bootstrap = true  

## Requirements
- Add fields if needed:
  - is_bootstrap
  - source
- Ensure seeded transactions are distinguishable from real transactions
- Bootstrap transactions must not be editable accidentally without warning

## Acceptance criteria
- Every holding can be represented as at least one bootstrap transaction
- The system can reconstruct holdings from transactions after bootstrap
- Bootstrap transactions are clearly marked
