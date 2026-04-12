from pydantic import BaseModel, field_validator


class OptionTradeCreate(BaseModel):
    """Request body for POST /api/options."""
    underlying_symbol: str
    option_type: str        # CALL or PUT
    action: str             # BUY or SELL
    strike: float
    expiration_date: str    # ISO YYYY-MM-DD
    quantity: int           # number of contracts
    open_date: str          # ISO YYYY-MM-DD
    open_price: float       # premium per share
    open_commission: float = 0.0
    exit_date: str | None = None
    exit_price: float | None = None
    close_commission: float = 0.0
    status: str = "OPEN"    # OPEN, CLOSED, or EXPIRED
    net_pnl: float | None = None
    notes: str | None = None

    @field_validator("option_type")
    @classmethod
    def validate_option_type(cls, v: str) -> str:
        if v not in ("CALL", "PUT"):
            raise ValueError("option_type must be CALL or PUT")
        return v

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        if v not in ("BUY", "SELL"):
            raise ValueError("action must be BUY or SELL")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in ("OPEN", "CLOSED", "EXPIRED"):
            raise ValueError("status must be OPEN, CLOSED, or EXPIRED")
        return v

    @field_validator("strike", "open_price")
    @classmethod
    def validate_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("must be positive")
        return v

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("quantity must be positive")
        return v


class OptionTradeUpdate(BaseModel):
    """Request body for PATCH /api/options/{id}. Underlying symbol is not editable."""
    option_type: str
    action: str
    strike: float
    expiration_date: str
    quantity: int
    open_date: str
    open_price: float
    open_commission: float = 0.0
    exit_date: str | None = None
    exit_price: float | None = None
    close_commission: float = 0.0
    status: str = "OPEN"
    net_pnl: float | None = None
    notes: str | None = None

    @field_validator("option_type")
    @classmethod
    def validate_option_type(cls, v: str) -> str:
        if v not in ("CALL", "PUT"):
            raise ValueError("option_type must be CALL or PUT")
        return v

    @field_validator("action")
    @classmethod
    def validate_action(cls, v: str) -> str:
        if v not in ("BUY", "SELL"):
            raise ValueError("action must be BUY or SELL")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in ("OPEN", "CLOSED", "EXPIRED"):
            raise ValueError("status must be OPEN, CLOSED, or EXPIRED")
        return v

    @field_validator("strike", "open_price")
    @classmethod
    def validate_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("must be positive")
        return v

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("quantity must be positive")
        return v


class OptionTradeRead(BaseModel):
    id: str
    underlying_symbol: str
    underlying_name: str
    option_type: str        # CALL or PUT
    action: str             # BUY or SELL
    strike: float
    expiration_date: str
    quantity: int
    open_date: str
    open_price: float
    open_commission: float
    exit_date: str | None
    exit_price: float | None
    close_commission: float
    status: str             # OPEN, CLOSED, EXPIRED
    net_pnl: float | None
    pnl_type: str           # "cash" for open positions, "realized" for closed/expired
    premium_cost: float     # Signed premium paid/received: BUY negative, SELL positive
    notes: str | None

    model_config = {"from_attributes": True}


class UnderlyingPnlSummary(BaseModel):
    symbol: str
    name: str
    trade_count: int
    closed_count: int
    expired_count: int
    open_count: int
    total_net_pnl: float
    win_count: int          # trades with net_pnl > 0
    win_rate: float         # win_count / (closed + expired)


class OptionsSummary(BaseModel):
    trades: list[OptionTradeRead]
    total_net_pnl: float
    trade_count: int
    closed_count: int
    expired_count: int
    open_count: int
    win_rate: float                         # % of closed+expired with positive P&L
    pnl_by_underlying: list[UnderlyingPnlSummary]


class ExpiredOptionResult(BaseModel):
    option_id: str
    symbol: str
    option_type: str
    action: str
    strike: float
    expiration_date: str
    quantity: int
    itm: bool
    shares_delivered: int   # contracts * 100 if ITM, else 0
    cash_delta: float       # positive = cash received, negative = cash paid


class ProcessExpiredResult(BaseModel):
    processed: int
    details: list[ExpiredOptionResult]
    cash_balance: float     # total portfolio cash balance after processing
