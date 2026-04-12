
# Recalculate portfolio allocation automatically

## TL;DR
Allocation percentages must update automatically when holdings change.

## Type
Feature

## Priority
Medium

## Effort
Medium

## Current behavior
Allocation is static until manual refresh.

## Expected behavior
Allocation recalculates whenever holdings change.

allocation_pct = holding_value / portfolio_value

## Requirements
- Recalculate allocation after holdings update
- Ensure allocation sums to 100%
- Trigger frontend refresh

## Acceptance criteria
- Adding transaction updates allocation
- Editing transaction updates allocation
- Deleting transaction updates allocation
