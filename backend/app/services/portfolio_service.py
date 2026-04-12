"""
Portfolio service — computes all derived values for holdings.

Rules:
  - cost_basis_usd     = quantity * avg_cost_usd
  - current_value_usd  = quantity * current_price_usd   (None if no price cached)
  - unrealized_pnl_usd = current_value_usd - cost_basis_usd
  - unrealized_pnl_pct = unrealized_pnl_usd / cost_basis_usd
  - allocation_pct     = current_value_usd / total_portfolio_value
"""

from sqlalchemy.orm import Session

from app.repositories import holding_repo
from app.schemas.holding import HoldingRead, PortfolioSummary
from app.services import market_data_service


def get_portfolio_summary(db: Session) -> PortfolioSummary:
    holdings = holding_repo.get_all_with_asset(db)

    from app.services.option_service import get_portfolio_cash_and_pnl
    realized = get_portfolio_cash_and_pnl(db)
    cash_balance = realized.total_cash

    if not holdings:
        return PortfolioSummary(
            holdings=[],
            total_cost_usd=0.0,
            total_value_usd=None,
            total_unrealized_pnl_usd=None,
            total_unrealized_pnl_pct=None,
            price_last_updated=None,
            has_stale_prices=False,
            cash_balance_usd=cash_balance,
            realized=realized,
        )

    symbols_with_currency = [(h.asset.symbol, h.asset.currency) for h in holdings]
    symbols = [s for s, _ in symbols_with_currency]

    price_data = market_data_service.get_cached_prices(db, symbols)

    enriched: list[HoldingRead] = []
    total_cost = 0.0
    total_value = 0.0
    any_price_missing = False
    has_stale = False

    # First pass: compute per-holding values
    items = []
    for holding in holdings:
        asset = holding.asset
        symbol = asset.symbol
        pd = price_data.get(symbol, {})

        cost_basis = holding.quantity * holding.avg_cost_usd
        total_cost += cost_basis

        price_usd = pd.get("price_usd")
        if price_usd is not None:
            current_value = holding.quantity * price_usd
            total_value += current_value
        else:
            current_value = None
            any_price_missing = True

        if pd.get("stale"):
            has_stale = True

        items.append({
            "holding": holding,
            "asset": asset,
            "cost_basis": cost_basis,
            "current_value": current_value,
            "price_usd": price_usd,
            "pd": pd,
        })

    # Determine latest fetched_at across all cached entries
    fetched_ats = [
        price_data[s]["fetched_at"]
        for s in symbols
        if price_data.get(s, {}).get("fetched_at")
    ]
    price_last_updated = max(fetched_ats) if fetched_ats else None

    # Unrealized P&L is equity-only (open stock positions vs their cost basis).
    # Option-derived cash and realized P&L are reported in the `realized` breakdown.
    total_unrealized_pnl = (total_value - total_cost) if not any_price_missing else None
    total_unrealized_pnl_pct = (
        (total_unrealized_pnl / total_cost) if total_unrealized_pnl is not None and total_cost > 0 else None
    )

    # Second pass: compute allocation_pct now that total_value is known
    for item in items:
        h = item["holding"]
        asset = item["asset"]
        cost_basis = item["cost_basis"]
        current_value = item["current_value"]
        price_usd = item["price_usd"]
        pd = item["pd"]

        unrealized_pnl = (current_value - cost_basis) if current_value is not None else None
        unrealized_pnl_pct = (
            (unrealized_pnl / cost_basis) if unrealized_pnl is not None and cost_basis > 0 else None
        )
        allocation_pct = (
            (current_value / total_value) if current_value is not None and total_value > 0 else None
        )

        enriched.append(
            HoldingRead(
                id=h.id,
                symbol=asset.symbol,
                name=asset.name,
                asset_type=asset.asset_type,
                exchange=asset.exchange,
                currency=asset.currency,
                quantity=h.quantity,
                avg_cost_usd=h.avg_cost_usd,
                avg_cost_native=h.avg_cost_native,
                cost_basis_usd=cost_basis,
                current_price_usd=price_usd,
                current_price_native=pd.get("price_native"),
                current_value_usd=current_value,
                unrealized_pnl_usd=unrealized_pnl,
                unrealized_pnl_pct=unrealized_pnl_pct,
                allocation_pct=allocation_pct,
                price_stale=pd.get("stale", True),
                price_fetched_at=pd.get("fetched_at"),
            )
        )

    return PortfolioSummary(
        holdings=enriched,
        total_cost_usd=total_cost,
        total_value_usd=total_value if not any_price_missing else None,
        total_unrealized_pnl_usd=total_unrealized_pnl,
        total_unrealized_pnl_pct=total_unrealized_pnl_pct,
        price_last_updated=price_last_updated,
        has_stale_prices=has_stale,
        cash_balance_usd=cash_balance,
        realized=realized,
    )
