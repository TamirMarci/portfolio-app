# Automatically Update Holdings When Transactions Change

## TL;DR
Implement real-time synchronization between transactions and holdings to ensure holdings always reflect aggregated transaction data.

## Type
Feature

## Priority
normal

## Effort
medium

## Current behavior
- Holdings are imported directly from Excel and remain static
- Transactions are imported separately but do not trigger updates to holdings
- Holdings do not reflect aggregated transaction calculations

## Expected behavior
- Holdings should be dynamically calculated from aggregated transactions
- Any change to transactions (add, update, import) should automatically update corresponding holdings, including quantity and average price
- If a holding doesn't exist for a transaction's symbol, it should be created
- Portfolio totals must remain consistent

## Relevant files
- backend/app/services/portfolio_service.py
- backend/app/repositories/holding_repo.py
- backend/app/repositories/transaction_repo.py

## Risks/dependencies
- Requires modifying the import pipeline to calculate holdings from transactions instead of direct import
- Ensure backward compatibility with existing Excel imports
- Potential impact on performance for large transaction histories

## Acceptance criteria
- Holdings quantity and average cost match the aggregated sum of all BUY/SELL transactions for each symbol
- Importing transactions via Excel updates holdings accordingly
- Holdings with zero quantity from transactions are removed or marked inactive
- Portfolio total value calculations remain accurate after transaction changes
- No duplicate holdings created for the same symbol
- Changes are idempotent (running import multiple times produces same result)