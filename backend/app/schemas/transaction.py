from pydantic import BaseModel, field_validator


class TransactionCreate(BaseModel):
    """Request body for POST /api/transactions."""
    symbol: str
    type: str           # BUY or SELL
    quantity: float
    price_per_share: float
    price_usd: float | None = None  # explicit USD price; auto-set for USD assets if omitted
    trade_date: str     # ISO YYYY-MM-DD
    fees: float = 0.0
    notes: str | None = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in ("BUY", "SELL"):
            raise ValueError("type must be BUY or SELL")
        return v

    @field_validator("quantity", "price_per_share")
    @classmethod
    def validate_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("must be positive")
        return v


class TransactionUpdate(BaseModel):
    """Request body for PATCH /api/transactions/{id}. Symbol is not editable."""
    type: str
    quantity: float
    price_per_share: float
    price_usd: float | None = None
    trade_date: str
    fees: float = 0.0
    notes: str | None = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in ("BUY", "SELL"):
            raise ValueError("type must be BUY or SELL")
        return v

    @field_validator("quantity", "price_per_share")
    @classmethod
    def validate_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("must be positive")
        return v


class TransactionRead(BaseModel):
    id: str
    symbol: str
    name: str
    asset_type: str
    type: str           # BUY or SELL
    quantity: float
    price_per_share: float
    price_usd: float | None
    trade_date: str
    fees: float
    notes: str | None

    # FX field
    fx_rate_to_usd: float | None

    # Bootstrap/seed fields
    is_bootstrap: bool
    source: str | None

    # Computed by service for SELL transactions (requires buy price from holdings)
    realized_pnl_usd: float | None
    realized_pnl_pct: float | None

    model_config = {"from_attributes": True}


class TransactionList(BaseModel):
    transactions: list[TransactionRead]
    total_count: int
