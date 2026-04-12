"""
Parser for Snapshot_YYYY sheets.

Auto-detection: any sheet whose name matches the pattern "Snapshot_DDDD"
is treated as a year-end portfolio snapshot. The snapshot date is derived
as YYYY-12-31.

The sheet structure mirrors Holdings (same columns, same derived-value
columns that are dropped). Company names may contain embedded ticker
symbols and non-breaking spaces — cleaned by name_cleaner.

NOTE: The Snapshot sheet does NOT have a Symbol column. The company name
contains the symbol in parentheses, e.g. "NVIDIA Corporation - (NVDA)".
We extract the symbol from the name using a regex.
"""

import re
import openpyxl
from dataclasses import dataclass

from importer.normalizers.name_cleaner import clean_name


_SYMBOL_IN_NAME_RE = re.compile(r"\(([A-Za-z0-9.]+)\)\s*$")


@dataclass
class RawSnapshotHolding:
    symbol: str
    company: str
    avg_cost_native: float
    quantity: float
    price_at_snapshot: float
    value_usd: float


@dataclass
class RawSnapshot:
    year: int
    snapshot_date: str          # YYYY-12-31
    label: str
    holdings: list[RawSnapshotHolding]


def is_snapshot_sheet(sheet_name: str) -> bool:
    return bool(re.match(r"^Snapshot_\d{4}$", sheet_name, re.IGNORECASE))


def extract_year(sheet_name: str) -> int:
    return int(sheet_name.split("_")[1])


def _extract_symbol_from_name(raw_name: str) -> tuple[str, str]:
    """Return (symbol, clean_name) extracted from a name like 'NVIDIA Corporation - (NVDA)'."""
    match = _SYMBOL_IN_NAME_RE.search(raw_name)
    symbol = match.group(1) if match else ""
    clean = clean_name(raw_name)
    return symbol, clean


def parse(ws: openpyxl.worksheet.worksheet.Worksheet, sheet_name: str) -> RawSnapshot:
    year = extract_year(sheet_name)
    snapshot_date = f"{year}-12-31"
    label = f"EOY {year}"

    rows = list(ws.iter_rows(min_row=1, values_only=True))
    if not rows:
        return RawSnapshot(year=year, snapshot_date=snapshot_date, label=label, holdings=[])

    headers = {str(v).strip().lower(): i for i, v in enumerate(rows[0]) if v is not None}

    holdings: list[RawSnapshotHolding] = []
    for row in rows[1:]:
        if not any(row):
            continue

        raw_company = row[headers.get("company", -1)]
        if not raw_company:
            continue

        symbol, company = _extract_symbol_from_name(str(raw_company))
        if not symbol:
            continue

        avg_cost = float(row[headers.get("avg cost/share", -1)] or 0)
        quantity = float(row[headers.get("current quantity", -1)] or 0)
        price_at_snapshot = float(row[headers.get("current price", -1)] or 0)
        value_usd = float(row[headers.get("current capital usd", -1)] or 0)

        if quantity <= 0:
            continue

        holdings.append(RawSnapshotHolding(
            symbol=symbol,
            company=company,
            avg_cost_native=avg_cost,
            quantity=quantity,
            price_at_snapshot=price_at_snapshot,
            value_usd=value_usd,
        ))

    return RawSnapshot(
        year=year,
        snapshot_date=snapshot_date,
        label=label,
        holdings=holdings,
    )
