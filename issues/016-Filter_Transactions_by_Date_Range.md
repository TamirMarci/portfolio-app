# Filter Transactions by Date Range

## TL;DR
Add date range filtering to the transactions page, with preset options for past month, week, year, and year-to-date.

## Type
Feature

## Priority
Normal

## Effort
Medium

---

## Current Behavior
- Transactions page lists all transactions without date filtering.
- No UI controls for date ranges.

## Expected Behavior
- Dropdown or buttons for preset date ranges: Past Month, Past Week, Past Year, Year-to-Date.
- Custom date picker for start/end dates.
- Filtered transactions update dynamically via API query params.
- Defaults to no filter (all transactions).

---

## Relevant Files
- `backend/app/routers/transactions.py` — Add query params `start_date`, `end_date` to `GET /api/transactions`
- `frontend/src/pages/Transactions.tsx` — Add filter UI components and integrate with React Query
- `frontend/src/api/types.ts` — Ensure date types match backend

---

## Risks & Dependencies
- Backend query needs efficient indexing on `trade_date` in `transactions` table.
- Frontend cache key should include date params to avoid stale data.
- Date handling: Use ISO strings (e.g., `2023-01-01`) for API consistency.

---

## Acceptance Criteria
- [ ] `GET /api/transactions?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` filters by `trade_date` range
- [ ] Preset buttons calculate dates client-side (e.g., Past Month: today - 30 days)
- [ ] Custom date picker uses a library like react-datepicker
- [ ] Filtered results update without page reload; React Query cache handles params
- [ ] UI shows active filter and clear option
- [ ] Unit tests for backend filtering logic
