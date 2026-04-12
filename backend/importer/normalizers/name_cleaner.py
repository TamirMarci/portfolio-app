"""
Company name cleaner.

The Snapshot_2025 sheet stores names like:
  "NVIDIA Corporation - (NVDA)"
  "Digi Power X Inc.\xa0(DGXX)"

This module strips those suffixes and any non-breaking space characters.
"""

import re

# Matches trailing patterns like " - (NVDA)", "  (DGXX)", " – (OCO.V)"
_SYMBOL_SUFFIX_RE = re.compile(r"[\s\xa0]*[-–]?[\s\xa0]*\([\w.]+\)\s*$")


def clean_name(name: str | None) -> str:
    if not name:
        return ""
    # Replace non-breaking spaces with regular spaces
    name = name.replace("\xa0", " ").replace("\u200b", "")
    # Strip trailing "(SYMBOL)" or "- (SYMBOL)" patterns
    name = _SYMBOL_SUFFIX_RE.sub("", name)
    return name.strip()
