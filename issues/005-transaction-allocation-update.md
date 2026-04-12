# Adding transactions does not update portfolio allocation percentages

## TL;DR
When new transactions are added, the allocation_pct field in holdings is not recalculated, leading to stale allocation data.

## Type
Bug

## Priority
Normal

## Effort
Medium

## Current behavior
- Transactions are added successfully and holdings are updated
- Allocation percentages (allocation_pct) remain unchanged until manual refresh or restart
- Frontend shows outdated allocation data

## Expected behavior
- After adding a transaction, allocation_pct should be recalculated for all holdings
- Allocation should reflect the new portfolio composition immediately
- No manual refresh required to see updated allocations

## Relevant files
- [backend/app/services/transaction_service.py](backend/app/services/transaction_service.py)
- [backend/app/services/portfolio_service.py](backend/app/services/portfolio_service.py)
- [frontend/src/pages/Allocation.tsx](frontend/src/pages/Allocation.tsx)

## Risks/dependencies
- Recalculation must be efficient to avoid performance issues with large portfolios
- Ensure allocation calculation is consistent across all services
- May need to update holdings after transaction operations

## Acceptance criteria
- Add a BUY transaction for a new symbol: allocation_pct updates for all holdings
- Add a SELL transaction: allocation_pct reflects reduced position
- Allocation percentages sum to 100% after recalculation
- Frontend Allocation page shows updated percentages without refresh</content>
<parameter name="filePath">c:\Users\orilu\Desktop\Tamir\MyProject\issues\transaction-allocation-update.md