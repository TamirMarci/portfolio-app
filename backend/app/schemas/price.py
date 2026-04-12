from typing import Literal
from pydantic import BaseModel


class PriceCacheRead(BaseModel):
    symbol: str
    price_usd: float
    price_native: float | None
    native_currency: str | None
    fetched_at: str
    source: str | None

    model_config = {"from_attributes": True}


class SymbolRefreshDetail(BaseModel):
    """Per-symbol result returned by the price refresh endpoint."""
    symbol: str
    status: Literal["ok", "failed"]
    currency: str
    price_native: float | None   # raw price in the asset's native currency
    price_usd: float | None      # FX-converted USD price (None on failure)
    error: str | None            # human-readable reason when status == "failed"


class RefreshResult(BaseModel):
    total_attempted: int
    succeeded: int
    failed: int
    per_symbol: list[SymbolRefreshDetail]
    fetched_at: str
    message: str
