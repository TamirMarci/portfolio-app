# Handle Expired Options and Physical Delivery Impact on Holdings

## TL;DR
Automatically detect expired option contracts, determine whether they expired in or out of the money, update their status to `EXPIRED`, and if they expired in the money, apply assumed physical delivery to portfolio holdings and cash.

---

## Type
Feature

## Priority
High

## Effort
Medium

---

# Current Behavior

- Option trades can remain in `OPEN` status even after their expiry date has passed.
- The system does not automatically evaluate expired options.
- The system does not determine whether an expired contract finished in or out of the money.
- The system does not apply physical delivery impact to holdings.
- The dashboard does not reflect resulting cash from exercised / assigned expiry outcomes.

Example:
- Today is 2026-04-12
- There is an option on `SEDG` with expiry date `2026-03-27`
- The option is still marked as `OPEN`
- This is incorrect because expiry has already passed

---

# Expected Behavior

For any option trade whose expiry date has passed and whose status is still `OPEN`, the system should:

1. Detect that the contract has expired
2. Determine whether it expired:
   - in the money
   - out of the money
3. Change the trade status from `OPEN` to `EXPIRED`
4. If expired in the money:
   - assume physical delivery for MVP
   - apply the resulting stock movement to holdings
   - apply the resulting cash movement to portfolio cash
5. If expired out of the money:
   - mark as `EXPIRED`
   - do not change holdings

---

# MVP Business Rule

For MVP, assume all contracts are handled as **physical delivery** when they expire in the money.

This means the system should convert the expired option outcome into a stock transaction effect on the portfolio.

Example from current portfolio:
- Underlying: `SEDG`
- Option expired in the money
- Strike: `41.5`
- Quantity: `2` contracts
- Contract multiplier: `100`

Result:
- 200 shares should be delivered
- Effective stock sale price = `41.5`
- If these were covered call shares, holdings should be reduced by 200 shares
- Cash should increase accordingly

---

# Scope for This Issue

## Part 1: Detect expired open options

The system should identify all option trades where:
- `status = OPEN`
- `expiry_date < today`

These trades must be re-evaluated.

---

## Part 2: Determine in-the-money vs out-of-the-money

The system should determine whether the contract expired ITM or OTM using the underlying price at expiry.

For MVP:
- Use the underlying closing price on expiry date if available
- If exact historical close is not yet supported, use the most reliable available fallback and document it clearly

Rules:
- Call is ITM if underlying price at expiry > strike
- Put is ITM if underlying price at expiry < strike

---

## Part 3: Update option status

After evaluation:
- expired contracts should no longer remain `OPEN`
- set status to `EXPIRED`

Optional future improvement:
- distinguish between `EXPIRED_OTM` and `EXPIRED_ITM`
- for MVP, `EXPIRED` is enough if the delivery effect is correctly applied

---

## Part 4: Apply physical delivery effect

If the expired contract finished in the money:

### Covered Call / Short Call scenario
Assume assignment and physical delivery.

Effect:
- reduce holdings of the underlying by `contracts * 100`
- increase cash by `strike * contracts * 100`

Example:
- 2 call contracts
- strike = 41.5
- shares delivered = 200
- cash added = 8,300

If holdings for that symbol become zero:
- remove the holding row or mark it inactive

If the delivered quantity equals the full current holding:
- the holding should disappear from holdings

---

# Important Portfolio Rules

- Holdings must stay consistent after assignment
- Cash must be updated and visible in the main dashboard
- Holdings should never become silently inconsistent with options outcome
- Expired option processing should be idempotent:
  - running the process multiple times must not apply delivery twice

---

# Dashboard Requirement

After physical delivery is applied:
- the main dashboard should show updated cash balance
- holdings should reflect reduced or removed share count
- if the underlying holding reaches zero, it should no longer appear as an active holding row

---

# Example Acceptance Scenario

Given:
- Today = 2026-04-12
- Option: short call on `SEDG`
- Expiry = 2026-03-27
- Strike = 41.5
- Quantity = 2 contracts
- Status = `OPEN`
- Portfolio currently holds 200 shares of `SEDG`

When expired option processing runs:
- The system detects the expiry date has passed
- It checks whether the option expired ITM
- If ITM:
  - status becomes `EXPIRED`
  - 200 shares are removed from holdings
  - cash increases by 8,300
  - `SEDG` holding row is removed if quantity becomes zero
  - cash is displayed in dashboard

---

# Relevant Files

Potential backend files:
- backend/app/services/options_service.py
- backend/app/services/portfolio_service.py
- backend/app/services/holding_service.py
- backend/app/repositories/options_repo.py
- backend/app/repositories/holding_repo.py
- backend/app/repositories/transaction_repo.py

Potential frontend files:
- options page
- dashboard page
- holdings display components

---

# Risks / Dependencies

- Requires reliable price lookup for option expiry evaluation
- Need a clear source for historical underlying price on expiry date
- Must avoid double-processing expired options
- Need to decide how portfolio cash is modeled if cash support does not already exist
- Need to ensure assignment logic only applies to relevant option types / positions
- Need to confirm current options model contains enough data:
  - option type (call/put)
  - action / side (buy/sell)
  - strike
  - expiry
  - quantity
  - underlying symbol

---

# Suggested Implementation Notes

- Add a backend routine that evaluates expired open options
- Trigger it in one of these ways:
  - during portfolio refresh
  - during options page load
  - via dedicated reconciliation routine
- Keep the processing deterministic and idempotent
- Persist a flag / timestamp / lifecycle marker if needed to ensure physical delivery is not applied twice

---

# Acceptance Criteria

- [ ] Open option contracts with expiry date in the past are detected
- [ ] Expired contracts are evaluated as ITM or OTM
- [ ] Expired open contracts are updated from `OPEN` to `EXPIRED`
- [ ] OTM expired contracts do not affect holdings
- [ ] ITM expired contracts apply assumed physical delivery for MVP
- [ ] Covered call assignment reduces the underlying holding by `contracts * 100`
- [ ] Cash increases by `strike * contracts * 100` when assigned
- [ ] If holdings quantity becomes zero, the holding is removed or marked inactive
- [ ] Dashboard displays updated cash balance
- [ ] Re-running the expired options process does not apply delivery twice
- [ ] Example case: 2 SEDG contracts at 41.5 correctly removes 200 shares and adds 8,300 cash if expired ITM