
# Deprecate Excel holdings as source of truth

## TL;DR
Remove the dependency on Excel Holdings as the authoritative portfolio state.

## Type
Migration

## Priority
Medium

## Effort
Medium

## Current behavior
Importer loads holdings directly from Excel.

## Target behavior
Excel is used only for initial migration.

Holdings are derived from transactions.

## Requirements
- Prevent holdings import from overwriting derived holdings
- Keep snapshots import intact
- Document Excel as migration-only tool

## Acceptance criteria
- Holdings sheet no longer overwrites derived holdings
- Portfolio state is determined only by transactions
