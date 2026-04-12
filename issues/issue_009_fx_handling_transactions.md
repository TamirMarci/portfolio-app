
# Add FX-aware handling for non-USD transactions

## TL;DR
Transactions involving non-USD assets must store FX conversion to compute USD portfolio value correctly.

## Type
Core Feature

## Priority
High

## Effort
Medium

## Problem
Assets like OCO.V are priced in CAD.

Using native price as USD produces incorrect portfolio value.

## Expected behavior
Each transaction stores:

price_native  
currency  
fx_rate_to_usd  
price_usd

price_usd = price_native * fx_rate_to_usd

## Requirements
- Fetch FX rate during transaction creation
- Store FX rate with transaction
- Maintain native currency for display

## Acceptance criteria
- Non-USD assets have correct USD cost basis
- Portfolio value remains USD-based
