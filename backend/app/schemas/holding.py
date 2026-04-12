from pydantic import BaseModel


class PortfolioCashAndPnl(BaseModel):
    """
    Realized cash and P&L broken down by source.

    Cash buckets (where money actually lands):
      options_income_cash  — net premium from OTM expiry + closed option trades
      position_close_cash  — gross delivery proceeds from ITM assignment
                             (SELL CALL / BUY PUT: positive; BUY CALL / SELL PUT: negative)
      total_cash           — options_income_cash + position_close_cash

    P&L buckets (economic gain / loss):
      options_realized_pnl — net P&L on the option contract itself across all
                             closed and expired trades (premium ± close − commissions)
      stock_realized_pnl   — (strike − avg_cost_at_delivery) × shares for every
                             ITM assignment that resulted in a stock SELL
                             (SELL CALL and BUY PUT only; BUY CALL / SELL PUT add
                             shares to holdings — realized P&L deferred until those
                             shares are later sold)
      total_realized_pnl   — options_realized_pnl + stock_realized_pnl
    """
    options_income_cash: float
    position_close_cash: float
    total_cash: float

    options_realized_pnl: float
    stock_realized_pnl: float
    total_realized_pnl: float


class HoldingRead(BaseModel):
    id: str
    symbol: str
    name: str
    asset_type: str
    exchange: str | None
    currency: str

    quantity: float
    avg_cost_usd: float
    avg_cost_native: float | None
    cost_basis_usd: float          # quantity * avg_cost_usd — computed by service

    current_price_usd: float | None
    current_price_native: float | None
    current_value_usd: float | None    # quantity * current_price_usd
    unrealized_pnl_usd: float | None   # current_value - cost_basis
    unrealized_pnl_pct: float | None   # unrealized_pnl / cost_basis
    allocation_pct: float | None       # current_value / total_portfolio_value

    price_stale: bool
    price_fetched_at: str | None

    model_config = {"from_attributes": True}


class PortfolioSummary(BaseModel):
    holdings: list[HoldingRead]
    total_cost_usd: float
    total_value_usd: float | None          # equity market value (stocks only, no cash)
    total_unrealized_pnl_usd: float | None # equity unrealized P&L only
    total_unrealized_pnl_pct: float | None
    price_last_updated: str | None
    has_stale_prices: bool
    cash_balance_usd: float                # = realized.total_cash (backward compat)
    realized: PortfolioCashAndPnl          # full cash + P&L breakdown
