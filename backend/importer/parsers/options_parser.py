"""
Parser for the Options sheet.

Expected columns:
  Underlying Symbol, Date, Type, Action, Strike, Expiration Date,
  Quantity, Price, Total Cost/Credit, Commissions Open,
  Exit Date, Exit Price, Commissions Close, Status, Net P&L

Notes:
  - "Total Cost/Credit" and unnamed "Total Profit" columns are dropped.
  - "00/01/1900" in Exit Date is treated as null (no exit yet).
  - Status values normalized to uppercase: OPEN, CLOSED, EXPIRED.
"""

import openpyxl
from dataclasses import dataclass
from importer.normalizers.date_normalizer import normalize_date


@dataclass
class RawOptionTrade:
    underlying_symbol: str
    option_type: str       # CALL or PUT
    action: str            # BUY or SELL
    strike: float
    expiration_date: str   # ISO date
    quantity: int
    open_date: str         # ISO date
    open_price: float
    open_commission: float
    exit_date: str | None  # ISO date or None
    exit_price: float | None
    close_commission: float
    status: str            # OPEN, CLOSED, EXPIRED
    net_pnl: float | None


def parse(ws: openpyxl.worksheet.worksheet.Worksheet) -> list[RawOptionTrade]:
    rows = list(ws.iter_rows(min_row=1, values_only=True))
    if not rows:
        return []

    headers = {str(v).strip().lower(): i for i, v in enumerate(rows[0]) if v is not None}

    results: list[RawOptionTrade] = []

    for row in rows[1:]:
        if not any(row):
            continue

        underlying = row[headers.get("underlying symbol", -1)]
        if not underlying:
            continue

        option_type = str(row[headers.get("type", -1)] or "").strip().upper()
        action = str(row[headers.get("action", -1)] or "").strip().upper()
        strike = float(row[headers.get("strike", -1)] or 0)

        expiration_date = normalize_date(row[headers.get("expiration date", -1)])
        open_date = normalize_date(row[headers.get("date", -1)])

        if not expiration_date or not open_date:
            continue

        quantity = int(row[headers.get("quantity", -1)] or 0)
        open_price = float(row[headers.get("price", -1)] or 0)
        open_commission = float(row[headers.get("commissions open", -1)] or 0)

        raw_exit_date = row[headers.get("exit date", -1)]
        exit_date = normalize_date(raw_exit_date)

        exit_price_raw = row[headers.get("exit price", -1)]
        exit_price = float(exit_price_raw) if exit_price_raw is not None and exit_price_raw != 0 else None

        close_commission = float(row[headers.get("commissions close", -1)] or 0)

        status_raw = str(row[headers.get("status", -1)] or "").strip().upper()
        if status_raw not in ("OPEN", "CLOSED", "EXPIRED"):
            status_raw = "OPEN"

        net_pnl_raw = row[headers.get("net p&l", -1)]
        net_pnl = float(net_pnl_raw) if net_pnl_raw is not None else None

        results.append(RawOptionTrade(
            underlying_symbol=str(underlying).strip(),
            option_type=option_type,
            action=action,
            strike=strike,
            expiration_date=expiration_date,
            quantity=quantity,
            open_date=open_date,
            open_price=open_price,
            open_commission=open_commission,
            exit_date=exit_date,
            exit_price=exit_price,
            close_commission=close_commission,
            status=status_raw,
            net_pnl=net_pnl,
        ))

    return results
