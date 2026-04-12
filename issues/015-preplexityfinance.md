# Add external Perplexity Finance link per asset symbol

## TL;DR
Clicking on an asset symbol (e.g. SOXX, OCO.V) should open the corresponding Perplexity Finance page in a new tab.

## Type
Feature (Frontend + minor backend awareness)

## Priority
Low / Medium

## Effort
Small

## Current behavior
- Asset symbols are displayed as plain text across the app:
  - Holdings table
  - Transactions table
  - Options table
  - Snapshots
- No external navigation is available

## Expected behavior
- Asset symbols should be clickable
- Clicking a symbol opens a new browser tab to:

https://www.perplexity.ai/finance/{SYMBOL}

Examples:
- SOXX → https://www.perplexity.ai/finance/SOXX
- OCO.V → https://www.perplexity.ai/finance/OCO.V

## Requirements

### 1. Link generation
- Use the asset symbol exactly as stored (including suffixes like `.V`)
- URL format:

https://www.perplexity.ai/finance/{symbol}

- Do not modify or normalize the symbol unless necessary

### 2. Frontend changes
Update all relevant tables/components to render symbol as a link:

- Holdings table
- Transactions table
- Options table
- Snapshots table

Behavior:
- Symbol is displayed as clickable text (anchor `<a>` or clickable component)
- Opens in a new tab (`target="_blank"`)
- Use `rel="noopener noreferrer"` for security

### 3. UI/UX
- Keep styling consistent with current design (dark mode)
- Add subtle hover effect (underline or color change)
- Do NOT make it look like a button — keep it lightweight

### 4. Error handling
- If symbol is missing/null → render as plain text (no link)
- No need to validate symbol existence with Perplexity

### 5. Reusability
- Create a reusable component:

Example:
`AssetSymbolLink.tsx`

Props:
- symbol: string

Returns:
- clickable link to Perplexity

### 6. Optional (nice to have)
- Add tooltip:
  "Open in Perplexity Finance"

## Relevant files
- frontend/src/components/tables/TransactionsTable.tsx
- frontend/src/components/tables/OptionsTable.tsx
- frontend/src/components/tables/HoldingsTable.tsx
- frontend/src/pages/Snapshots.tsx

## Acceptance criteria
- All asset symbols are clickable
- Clicking opens correct Perplexity URL
- Works for symbols with suffixes (e.g. OCO.V)
- Opens in new tab
- No console errors
- UI remains clean and consistent