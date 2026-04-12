
# Add rebuild command for derived holdings

## TL;DR
Provide a command to rebuild holdings from transaction history.

## Type
Tooling

## Priority
Medium

## Effort
Medium

## Expected behavior
Command:

rebuild_holdings()

Steps:

1. Clear holdings table
2. Recalculate holdings from transactions
3. Validate portfolio integrity

## Integrity checks
- no negative quantities
- allocation sums correctly
- holdings match transaction totals

## Acceptance criteria
- Command rebuilds holdings deterministically
- Summary log shows results
