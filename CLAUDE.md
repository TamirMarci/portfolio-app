# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Personal portfolio tracker with an Excel import pipeline, a FastAPI backend, and a React frontend. Data originates from `Portfolio.xlsx` and is imported once (idempotently) into a local SQLite database. Live prices are fetched on demand from yfinance.

---

## Running the project

### Backend (from `backend/`)

```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload during development (always use --reload)
uvicorn app.main:app --port 8000 --reload

# The API is at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

**Important:** always use `--reload` during development. The backend must be restarted (or reload must be active) whenever Python files change — a stale server will silently serve old code.

### Frontend (from `frontend/`)

```bash
npm install
npm run dev     # dev server at http://localhost:5173
npm run build   # type-check + Vite production build
```

Vite proxies `/api/*` → `http://localhost:8000`, so both servers must be running simultaneously.

### Data import (from `backend/`)

```bash
# First import (or full reset)
python -m importer.run_import --reset

# Re-import transactional data only (keeps assets/holdings, re-imports transactions/options/snapshots)
python -m importer.run_import --reset-data

# Normal idempotent import (safe to run repeatedly)
python -m importer.run_import

# Custom Excel path
python -m importer.run_import --file /path/to/Portfolio.xlsx
```

---

## Architecture

### Backend layers (strictly top-down, no skipping layers)

```
routers/       HTTP endpoints — thin, delegate to services
services/      Business logic and derived computations
repositories/  All DB queries — plain functions, Session injected as arg
models/        SQLAlchemy ORM models (schema source of truth)
schemas/       Pydantic request/response models
```

Repositories use plain module-level functions (not classes). Every repo function takes `db: Session` as its first argument. `db.flush()` is called after writes inside a repo; `db.commit()` is called by the router or importer, not by repos or services.

### Key data flow: price refresh

`POST /api/prices/refresh` → `market_data_service.refresh_prices()` → per-symbol `yf.Ticker(symbol).fast_info.last_price` → `price_cache_repo.upsert()` → `db.commit()`. On success the frontend invalidates the `['holdings']` React Query cache key, triggering a background refetch of `GET /api/holdings`.

**Do not use `yf.download()`.** It was replaced with per-symbol `fast_info` calls because the DataFrame column layout changed between yfinance versions and exchange-suffix tickers (e.g. `OCO.V`) silently return NaN in batch mode.

### Import pipeline (from `importer/`)

Three-stage pipeline: `parsers/` → `normalizers/` → `loaders/`.

- `loaders/db_loader.py` is the only place that writes to the DB during import.
- All loaders return `LoadResult(inserted, skipped)`.
- **Holdings and assets:** always upserted (idempotent).
- **Transactions:** skip-if-exists checked against natural key `(asset_id, type, trade_date, quantity, price_per_share)`.
- **Option trades:** skip-if-exists checked against natural key `(underlying_asset_id, option_type, action, strike, expiration_date, open_date)`.
- **Snapshots:** skipped if same `snapshot_date` already exists.

### Database

SQLite at `backend/portfolio.db`. Schema is managed by SQLAlchemy `create_all` (not Alembic migrations). To apply model changes to an existing DB, run `--reset` (drops and recreates all tables).

**Unique constraints that exist in models (not just application logic):**
- `assets.symbol`
- `holdings.asset_id`
- `portfolio_snapshots.snapshot_date`
- `transactions`: `(asset_id, type, trade_date, quantity, price_per_share)`
- `option_trades`: `(underlying_asset_id, option_type, action, strike, expiration_date, open_date)`
- `snapshot_holdings`: `(snapshot_id, asset_id)`

### Frontend

React 18 + TypeScript + TanStack React Query v5 + Tailwind CSS. No global state manager — all server state is in React Query.

- All TypeScript API types live in `frontend/src/api/types.ts`. When the backend Pydantic schema changes, update this file to match.
- Query keys: `['holdings']`, `['transactions']`, `['options']`, `['snapshots']`.
- `PriceRefreshButton` is in `Layout.tsx` (persistent across all pages). It uses `useMutation`; on success it invalidates `['holdings']`.
- `formatters.ts` handles all number/date formatting; all formatters accept `null | undefined` and return `'—'`.

### FX handling

Non-USD assets (e.g. `OCO.V` in CAD) store `avg_cost_native` (original currency) and `avg_cost_usd` (FX-converted). `FX_TICKERS` in `market_data_service.py` maps ISO currency codes to yfinance FX tickers (`"CAD": "CADUSD=X"`). Add new currencies there when new non-USD assets are imported.

---

## Critical conventions

- **Schema changes require `--reset`** on the local SQLite DB — `create_all` does not migrate existing tables.
- **All API response shapes must stay in sync** between the Pydantic schema (`backend/app/schemas/`) and the TypeScript interface (`frontend/src/api/types.ts`). A mismatch causes runtime crashes in the frontend (not type errors — TypeScript types are erased at runtime).
- **Stub assets:** the importer creates minimal asset records (`asset_type="STOCK"`, `currency="USD"`) for symbols that appear in transactions or snapshots but are no longer in holdings (e.g. sold securities). These stubs have no associated holding row.
- **`db.flush()` vs `db.commit()`:** repos call `flush()` so the row gets an ID within the transaction; the caller (router or importer) commits. Never call `commit()` inside a repo or service.
