"""
Date normalization for all Excel sheets.

Handles:
  - String "DD.MM.YYYY"         → "YYYY-MM-DD"
  - datetime / date objects      → "YYYY-MM-DD"
  - "00/01/1900"                 → None  (Excel null date sentinel)
  - None / empty                 → None
"""

from datetime import datetime, date


_NULL_SENTINELS = {"00/01/1900", "01/00/1900", "00/00/1900", "0", ""}


def normalize_date(value) -> str | None:
    if value is None:
        return None

    # Already a date/datetime object from openpyxl
    if isinstance(value, datetime):
        # Catch Excel epoch sentinel (1900-01-00 parses as 1899-12-31 or 1900-01-01)
        if value.year < 1970:
            return None
        return value.strftime("%Y-%m-%d")

    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")

    text = str(value).strip()

    if text in _NULL_SENTINELS:
        return None

    # Try DD.MM.YYYY  (our primary format from manual Excel entry)
    for fmt in ("%d.%m.%Y", "%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue

    return None
