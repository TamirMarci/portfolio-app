"""
Parser for the Holdings sheet.

Expected columns (by name, case-insensitive):
  Company, Symbol, Asset Type, Exchange, Currency,
  Avg Cost/Share, Current quantity

Columns intentionally dropped (derived values — computed at runtime):
  Cost, % Cost basis, Current Price, Current Capital USD,
  Overall Yield %, % Current
"""

import openpyxl
from dataclasses import dataclass


@dataclass
class RawHolding:
    company: str
    symbol: str
    asset_type: str
    exchange: str | None
    currency: str
    avg_cost_native: float   # in asset's native currency
    quantity: float


def parse(ws: openpyxl.worksheet.worksheet.Worksheet) -> list[RawHolding]:
    rows = list(ws.iter_rows(min_row=1, values_only=True))
    if not rows:
        return []

    # Build column index from header row (case-insensitive, strip whitespace)
    headers = {str(v).strip().lower(): i for i, v in enumerate(rows[0]) if v is not None}

    required = {"company", "symbol", "avg cost/share", "current quantity"}
    missing = required - set(headers)
    if missing:
        raise ValueError(f"Holdings sheet missing required columns: {missing}")

    results: list[RawHolding] = []
    for row in rows[1:]:
        if not any(row):
            continue

        symbol = row[headers["symbol"]]
        if not symbol:
            continue

        company = str(row[headers["company"]] or "").strip()
        asset_type = str(row[headers.get("asset type", headers.get("asset_type", -1))] or "STOCK").strip().upper()
        exchange = str(row[headers.get("exchange", -1)] or "").strip() or None
        currency = str(row[headers.get("currency", -1)] or "USD").strip().upper()
        avg_cost = float(row[headers["avg cost/share"]] or 0)
        quantity = float(row[headers["current quantity"]] or 0)

        if quantity <= 0:
            continue

        results.append(RawHolding(
            company=company,
            symbol=str(symbol).strip(),
            asset_type=asset_type,
            exchange=exchange,
            currency=currency if currency else "USD",
            avg_cost_native=avg_cost,
            quantity=quantity,
        ))

    return results
