# Implement MVP-level options P&L calculation

## TL;DR
Add correct, clearly labeled MVP-level P&L calculations for option trades, without pretending to support full mark-to-market or broker-grade options accounting.

## Type
Feature

## Priority
Normal

## Effort
Medium

## Current behavior
- Options trades currently store `net_pnl` imported from Excel or entered manually
- No consistent backend calculation exists based on trade details
- Frontend displays `net_pnl` without distinguishing between realized P&L and cash impact

## Expected behavior
- OPEN options: calculate cash impact so far, not full unrealized mark-to-market
- CLOSED options: calculate realized net P&L from open/close cash flows and commissions
- EXPIRED options: calculate final realized P&L based on open action and premium
- Backend schemas clearly distinguish:
  - cash-only P&L for open positions
  - realized P&L for closed/expired positions
- Frontend displays these values with clear labels

## Calculation rules
Assume:
- `quantity` = number of option contracts
- contract multiplier = 100

Define:
- `open_cash_flow`
  - SELL:  +(open_price × quantity × 100)
  - BUY:   -(open_price × quantity × 100)

- `close_cash_flow`
  - if closing by BUY:
      -(exit_price × quantity × 100)
  - if closing by SELL:
      +(exit_price × quantity × 100)

Then:

### OPEN
- `net_pnl_cash = open_cash_flow - open_commission`
- This is cash impact only, not full mark-to-market

### CLOSED
- `realized_pnl = open_cash_flow + close_cash_flow - open_commission - close_commission`

### EXPIRED
If the position expired without a closing trade:
- sold option expired:
  - `realized_pnl = open_cash_flow - open_commission`
- bought option expired worthless:
  - `realized_pnl = open_cash_flow - open_commission`
  - (this will be negative, because open_cash_flow is negative)

## Constraints
- Do not add live option-chain pricing
- Do not add mark-to-market valuation for open options
- Do not add assignment/exercise logic
- Do not add Greeks or theoretical pricing
- Do not change holdings logic

## Relevant files
- [backend/app/services/option_service.py](backend/app/services/option_service.py)
- [backend/app/schemas/option.py](backend/app/schemas/option.py)
- [backend/importer/parsers/options_parser.py](backend/importer/parsers/options_parser.py)
- [frontend/src/components/tables/OptionsTable.tsx](frontend/src/components/tables/OptionsTable.tsx)

## Risks/dependencies
- Existing imported `net_pnl` values may differ from newly calculated values
- The UI should use calculated values as the source of truth
- Need to ensure BUY/SELL semantics are handled consistently
- Commission fields must be included correctly

## Acceptance criteria
- OPEN trades show a clearly labeled cash-only P&L value
- CLOSED trades show a clearly labeled realized P&L value
- EXPIRED trades show final realized P&L based on open action
- Frontend shows separate columns or labels for:
  - premium/cost
  - status
  - cash-only vs realized P&L
- Imported `net_pnl` is not blindly trusted if calculated values are available
- No live pricing, assignment, or Greeks are included