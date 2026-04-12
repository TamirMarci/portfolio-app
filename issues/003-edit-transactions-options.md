# Add ability to edit transactions and options

## TL;DR
Users cannot edit existing transactions and option trades; only add and delete are currently supported.

## Type
Feature

## Priority
Normal

## Effort
Medium

## Current behavior
- Transaction and options tables only show delete buttons
- No edit buttons or edit modals exist in the frontend
- Backend currently has create/delete flows, but no update endpoints for transactions and option trades

## Expected behavior
- Edit buttons appear in table rows for transactions and options
- Clicking edit opens a modal or form pre-filled with current values
- Users can modify editable fields and save changes
- Backend updates the record and returns updated data
- Tables refresh to show the updated values

## Constraints
- Do not recalculate holdings from transactions or options in this MVP
- Do not change the current source of truth for holdings
- Do not implement realized P&L logic as part of this feature
- Reuse existing create modals/forms where possible
- Keep the implementation minimal and consistent with the current architecture

## Relevant files
- [frontend/src/components/tables/TransactionsTable.tsx](frontend/src/components/tables/TransactionsTable.tsx)
- [frontend/src/components/tables/OptionsTable.tsx](frontend/src/components/tables/OptionsTable.tsx)
- [backend/app/routers/transactions.py](backend/app/routers/transactions.py)
- [backend/app/routers/options.py](backend/app/routers/options.py)
- [backend/app/services/transaction_service.py](backend/app/services/transaction_service.py)
- [backend/app/services/option_service.py](backend/app/services/option_service.py)
- [backend/app/schemas/transaction.py](backend/app/schemas/transaction.py)
- [backend/app/schemas/option.py](backend/app/schemas/option.py)

## Risks/dependencies
- Updates must preserve validation rules and database integrity
- Duplicate natural keys should return a clear validation error
- Forms should handle API failures gracefully

## Acceptance criteria
- Transaction table rows have an "Edit" button next to "Delete"
- Clicking "Edit" opens a modal with current transaction data pre-filled
- User can modify editable fields and save
- On save, transaction is updated via PUT or PATCH `/api/transactions/{id}`
- Table refreshes and shows updated transaction
- Similar functionality works for option trades via PUT or PATCH `/api/options/{id}`
- Validation and API errors are shown clearly in the UI
- Editing a transaction or option does not recalculate holdings