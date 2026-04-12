"""
Parser for the Transactions sheet.

Expected columns:
  ID, Symbol2, Type, Quant, Buy dates, Sell date,
  Buy price, Sell price, Fees, profit $, Yield

Notes:
  - "Symbol2" is treated as the asset symbol.
  - For a SELL row: trade_date = Sell date, price = Sell price.
  - "profit $" and "Yield" are derived — dropped (recomputed by service).
  - Date parsing handles both string "DD.MM.YYYY" and datetime objects.
"""

import openpyxl
from dataclasses import dataclass
from importer.normalizers.date_normalizer import normalize_date


@dataclass
class RawTransaction:
    symbol: str
    type: str          # BUY or SELL
    quantity: float
    price_per_share: float
    trade_date: str    # ISO YYYY-MM-DD
    fees: float


def parse(ws: openpyxl.worksheet.worksheet.Worksheet) -> list[RawTransaction]:
    rows = list(ws.iter_rows(min_row=1, values_only=True))
    if not rows:
        return []

    headers = {str(v).strip().lower(): i for i, v in enumerate(rows[0]) if v is not None}

    results: list[RawTransaction] = []

    for row in rows[1:]:
        if not any(row):
            continue

        # Symbol is in the "symbol2" column (Excel naming quirk)
        sym_idx = headers.get("symbol2") or headers.get("symbol")
        if sym_idx is None:
            continue

        symbol = row[sym_idx]
        if not symbol:
            continue

        tx_type = str(row[headers.get("type", -1)] or "").strip().upper()
        if tx_type not in ("BUY", "SELL"):
            continue

        quantity = float(row[headers.get("quant", headers.get("quantity", -1))] or 0)
        if quantity <= 0:
            continue

        fees = float(row[headers.get("fees", -1)] or 0)

        if tx_type == "SELL":
            raw_date = row[headers.get("sell date", -1)]
            price = float(row[headers.get("sell price", -1)] or 0)
        else:
            raw_date = row[headers.get("buy dates", headers.get("buy date", -1))]
            price = float(row[headers.get("buy price", -1)] or 0)

        trade_date = normalize_date(raw_date)
        if not trade_date:
            continue

        results.append(RawTransaction(
            symbol=str(symbol).strip(),
            type=tx_type,
            quantity=quantity,
            price_per_share=price,
            trade_date=trade_date,
            fees=fees,
        ))

    return results
