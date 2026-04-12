"""
Options service — aggregates option trade data and computes analytics.
"""

from collections import defaultdict
from datetime import date

from sqlalchemy.orm import Session

from app.repositories import option_repo, price_cache_repo, transaction_repo, holding_repo
from app.schemas.holding import PortfolioCashAndPnl
from app.schemas.option import (
    OptionTradeCreate, OptionTradeUpdate, OptionTradeRead, OptionsSummary, UnderlyingPnlSummary,
    ExpiredOptionResult, ProcessExpiredResult,
)
from app.services import market_data_service


def calculate_option_pnl(trade) -> float:
    """
    Calculate P&L for an option trade using explicit cash-flow semantics.
    Contract multiplier = 100.

    open_cash_flow:
        SELL: +(open_price × qty × 100)   — premium received
        BUY:  -(open_price × qty × 100)   — premium paid

    close_cash_flow (opposite action to open):
        opened BUY  → close by SELL: +(exit_price × qty × 100)
        opened SELL → close by BUY:  -(exit_price × qty × 100)

    OPEN:    net_pnl = open_cash_flow − open_commission
    CLOSED:  net_pnl = open_cash_flow + close_cash_flow − open_commission − close_commission
    EXPIRED: net_pnl = open_cash_flow − open_commission   (no closing trade)
    """
    multiplier = 100
    qty = trade.quantity

    # open_cash_flow: positive if selling (premium received), negative if buying (premium paid)
    open_cash_flow = trade.open_price * qty * multiplier
    if trade.action == 'BUY':
        open_cash_flow = -open_cash_flow

    if trade.status == 'OPEN':
        return open_cash_flow - (trade.open_commission or 0.0)

    if trade.status == 'CLOSED':
        if trade.exit_price is None:
            return 0.0
        # close_cash_flow: opposite direction to the opening trade
        close_cash_flow = trade.exit_price * qty * multiplier
        if trade.action == 'BUY':
            # opened BUY → close by SELL → positive close cash flow
            pass  # already positive
        else:
            # opened SELL → close by BUY → negative close cash flow
            close_cash_flow = -close_cash_flow
        return (
            open_cash_flow
            + close_cash_flow
            - (trade.open_commission or 0.0)
            - (trade.close_commission or 0.0)
        )

    if trade.status == 'EXPIRED':
        # No closing trade: same as OPEN formula — cash collected/paid minus open commission
        return open_cash_flow - (trade.open_commission or 0.0)

    return 0.0


def calculate_premium_cost(trade) -> float:
    """Calculate the signed premium cost: negative for bought, positive for sold."""
    multiplier = 100
    sign = -1 if trade.action == 'BUY' else 1
    return sign * trade.open_price * trade.quantity * multiplier


def get_pnl_type(status: str) -> str:
    """Return the P&L label for a given trade status."""
    return "cash" if status == "OPEN" else "realized"


def create_option_trade(db: Session, body: OptionTradeCreate) -> OptionTradeRead:
    """
    Resolve underlying asset by symbol and insert a new option trade.
    If the asset is not yet in the DB, it is fetched from yfinance and created automatically.
    Raises ValueError if the symbol cannot be resolved.
    """
    asset = market_data_service.get_or_create_asset(db, body.underlying_symbol)

    trade = option_repo.create(
        db,
        underlying_asset_id=asset.id,
        option_type=body.option_type,
        action=body.action,
        strike=body.strike,
        expiration_date=body.expiration_date,
        quantity=body.quantity,
        open_date=body.open_date,
        open_price=body.open_price,
        open_commission=body.open_commission,
        exit_date=body.exit_date,
        exit_price=body.exit_price,
        close_commission=body.close_commission,
        status=body.status,
        net_pnl=body.net_pnl,  # Will be overridden by calculation
        notes=body.notes,
    )

    # Calculate correct P&L
    calculated_pnl = calculate_option_pnl(trade)
    pnl_type = get_pnl_type(trade.status)

    # Update the trade with calculated values
    trade.net_pnl = calculated_pnl
    db.flush()

    return OptionTradeRead(
        id=trade.id,
        underlying_symbol=asset.symbol,
        underlying_name=asset.name,
        option_type=trade.option_type,
        action=trade.action,
        strike=trade.strike,
        expiration_date=str(trade.expiration_date),
        quantity=trade.quantity,
        open_date=str(trade.open_date),
        open_price=trade.open_price,
        open_commission=trade.open_commission or 0.0,
        exit_date=str(trade.exit_date) if trade.exit_date else None,
        exit_price=trade.exit_price,
        close_commission=trade.close_commission or 0.0,
        status=trade.status,
        net_pnl=calculated_pnl,
        pnl_type=pnl_type,
        premium_cost=calculate_premium_cost(trade),
        notes=trade.notes,
    )


def update_option_trade(db: Session, option_id: str, body: OptionTradeUpdate) -> OptionTradeRead:
    """
    Update an existing option trade's fields (underlying symbol is not changeable).
    Raises ValueError if the trade does not exist.
    """
    trade = option_repo.get_by_id(db, option_id)
    if trade is None:
        raise ValueError(f"Option trade not found: {option_id}")

    asset = trade.underlying_asset

    trade = option_repo.update(
        db,
        trade,
        option_type=body.option_type,
        action=body.action,
        strike=body.strike,
        expiration_date=body.expiration_date,
        quantity=body.quantity,
        open_date=body.open_date,
        open_price=body.open_price,
        open_commission=body.open_commission,
        exit_date=body.exit_date,
        exit_price=body.exit_price,
        close_commission=body.close_commission,
        status=body.status,
        net_pnl=body.net_pnl,  # Will be overridden
        notes=body.notes,
    )

    # Recalculate P&L
    calculated_pnl = calculate_option_pnl(trade)
    pnl_type = get_pnl_type(trade.status)

    trade.net_pnl = calculated_pnl
    db.flush()

    return OptionTradeRead(
        id=trade.id,
        underlying_symbol=asset.symbol,
        underlying_name=asset.name,
        option_type=trade.option_type,
        action=trade.action,
        strike=trade.strike,
        expiration_date=str(trade.expiration_date),
        quantity=trade.quantity,
        open_date=str(trade.open_date),
        open_price=trade.open_price,
        open_commission=trade.open_commission or 0.0,
        exit_date=str(trade.exit_date) if trade.exit_date else None,
        exit_price=trade.exit_price,
        close_commission=trade.close_commission or 0.0,
        status=trade.status,
        net_pnl=calculated_pnl,
        pnl_type=pnl_type,
        premium_cost=calculate_premium_cost(trade),
        notes=trade.notes,
    )


def delete_option_trade(db: Session, option_id: str) -> None:
    """
    Delete an option trade by ID.
    Raises ValueError if the trade does not exist.
    """
    trade = option_repo.get_by_id(db, option_id)
    if trade is None:
        raise ValueError(f"Option trade not found: {option_id}")
    option_repo.delete(db, trade)


def get_options_summary(db: Session) -> OptionsSummary:
    trades = option_repo.get_all_with_asset(db)

    trade_reads: list[OptionTradeRead] = []
    total_net_pnl = 0.0
    closed_count = 0
    expired_count = 0
    open_count = 0
    resolved_winning = 0
    resolved_total = 0

    # Aggregate by underlying symbol
    underlying_data: dict[str, dict] = defaultdict(lambda: {
        "name": "",
        "trade_count": 0,
        "closed_count": 0,
        "expired_count": 0,
        "open_count": 0,
        "total_net_pnl": 0.0,
        "win_count": 0,
    })

    for trade in trades:
        asset = trade.underlying_asset
        symbol = asset.symbol

        calculated_pnl = calculate_option_pnl(trade)
        pnl_type = get_pnl_type(trade.status)

        trade_read = OptionTradeRead(
            id=trade.id,
            underlying_symbol=symbol,
            underlying_name=asset.name,
            option_type=trade.option_type,
            action=trade.action,
            strike=trade.strike,
            expiration_date=str(trade.expiration_date),
            quantity=trade.quantity,
            open_date=str(trade.open_date),
            open_price=trade.open_price,
            open_commission=trade.open_commission or 0.0,
            exit_date=str(trade.exit_date) if trade.exit_date else None,
            exit_price=trade.exit_price,
            close_commission=trade.close_commission or 0.0,
            status=trade.status,
            net_pnl=calculated_pnl,
            pnl_type=pnl_type,
            premium_cost=calculate_premium_cost(trade),
            notes=trade.notes,
        )
        trade_reads.append(trade_read)

        net_pnl = calculated_pnl
        total_net_pnl += net_pnl

        ud = underlying_data[symbol]
        ud["name"] = asset.name
        ud["trade_count"] += 1
        ud["total_net_pnl"] += net_pnl

        status = trade.status.upper()
        if status == "CLOSED":
            closed_count += 1
            ud["closed_count"] += 1
            resolved_total += 1
            if net_pnl > 0:
                resolved_winning += 1
                ud["win_count"] += 1
        elif status == "EXPIRED":
            expired_count += 1
            ud["expired_count"] += 1
            resolved_total += 1
            if net_pnl > 0:
                resolved_winning += 1
                ud["win_count"] += 1
        else:
            open_count += 1
            ud["open_count"] += 1

    win_rate = (resolved_winning / resolved_total) if resolved_total > 0 else 0.0

    pnl_by_underlying = [
        UnderlyingPnlSummary(
            symbol=sym,
            name=data["name"],
            trade_count=data["trade_count"],
            closed_count=data["closed_count"],
            expired_count=data["expired_count"],
            open_count=data["open_count"],
            total_net_pnl=data["total_net_pnl"],
            win_count=data["win_count"],
            win_rate=(
                data["win_count"] / (data["closed_count"] + data["expired_count"])
                if (data["closed_count"] + data["expired_count"]) > 0
                else 0.0
            ),
        )
        for sym, data in underlying_data.items()
    ]

    # Sort by absolute P&L descending
    pnl_by_underlying.sort(key=lambda x: abs(x.total_net_pnl), reverse=True)

    return OptionsSummary(
        trades=trade_reads,
        total_net_pnl=total_net_pnl,
        trade_count=len(trade_reads),
        closed_count=closed_count,
        expired_count=expired_count,
        open_count=open_count,
        win_rate=win_rate,
        pnl_by_underlying=pnl_by_underlying,
    )


def get_portfolio_cash_and_pnl(db: Session) -> PortfolioCashAndPnl:
    """
    Derive all realized cash and P&L buckets from option trade history.
    Computed on-the-fly — no separate persistent balance; always consistent
    with the current state of the option_trades table.

    Cash buckets
    ------------
    options_income_cash
        Net premium from OTM expiry (premium kept) and closed option trades.
        Includes both long and short positions; negative if you closed at a loss.

    position_close_cash
        Gross delivery proceeds from ITM assignment.
        Sign convention:
          SELL CALL ITM  →  +strike × shares  (shares called away, receive cash)
          BUY  PUT  ITM  →  +strike × shares  (exercise, sell shares, receive cash)
          BUY  CALL ITM  →  -strike × shares  (exercise, buy shares, pay cash)
          SELL PUT  ITM  →  -strike × shares  (assigned shares, pay cash)

    P&L buckets
    -----------
    options_realized_pnl
        Net P&L of the option contract across all CLOSED and EXPIRED trades.
        = open_premium ± close_premium − commissions (per calculate_option_pnl).
        Intentionally excludes the stock-side gain/loss of ITM assignments.

    stock_realized_pnl
        (strike − delivery_avg_cost_usd) × shares for every ITM assignment
        that resulted in a stock SELL (SELL CALL and BUY PUT).
        BUY CALL / SELL PUT exercises add shares to holdings — stock P&L
        is deferred to when those shares are eventually sold.
        delivery_avg_cost_usd is captured at the moment of assignment and
        stored on the OptionTrade row.

    ITM detection
    -------------
    An EXPIRED trade is considered ITM iff trade.delivery_avg_cost_usd IS NOT NULL.
    That field is only set inside process_expired_options when delivery is applied.
    """
    trades = option_repo.get_all_with_asset(db)

    options_income_cash = 0.0
    position_close_cash = 0.0
    options_realized_pnl = 0.0
    stock_realized_pnl = 0.0

    for trade in trades:
        if trade.status == "OPEN":
            continue

        option_pnl = calculate_option_pnl(trade)
        options_realized_pnl += option_pnl

        if trade.status == "CLOSED":
            # Entire net premium flow is income / expense
            options_income_cash += option_pnl

        elif trade.status == "EXPIRED":
            itm_assigned = trade.delivery_avg_cost_usd is not None

            if not itm_assigned:
                # OTM — option expired worthless; premium is the only cash flow
                options_income_cash += option_pnl

            else:
                # ITM — physical delivery was applied
                shares = trade.quantity * 100

                if trade.action == "SELL" and trade.option_type == "CALL":
                    # Covered call assigned: shares sold at strike → receive cash
                    position_close_cash += trade.strike * shares
                    stock_realized_pnl += (trade.strike - trade.delivery_avg_cost_usd) * shares

                elif trade.action == "BUY" and trade.option_type == "PUT":
                    # Long put exercised: shares sold at strike → receive cash
                    position_close_cash += trade.strike * shares
                    stock_realized_pnl += (trade.strike - trade.delivery_avg_cost_usd) * shares

                elif trade.action == "BUY" and trade.option_type == "CALL":
                    # Long call exercised: buy shares at strike → pay cash
                    # Stock P&L deferred (new shares added to holdings at strike cost)
                    position_close_cash -= trade.strike * shares

                elif trade.action == "SELL" and trade.option_type == "PUT":
                    # Short put assigned: forced to buy shares at strike → pay cash
                    # Stock P&L deferred (new shares added to holdings at strike cost)
                    position_close_cash -= trade.strike * shares

    return PortfolioCashAndPnl(
        options_income_cash=options_income_cash,
        position_close_cash=position_close_cash,
        total_cash=options_income_cash + position_close_cash,
        options_realized_pnl=options_realized_pnl,
        stock_realized_pnl=stock_realized_pnl,
        total_realized_pnl=options_realized_pnl + stock_realized_pnl,
    )


def process_expired_options(db: Session) -> ProcessExpiredResult:
    """
    Detect all OPEN options with expiration_date < today, mark them EXPIRED,
    and apply physical delivery for ITM contracts.

    Idempotency
    -----------
    Only OPEN options are queried. Once a trade is marked EXPIRED it cannot
    be processed again. delivery_avg_cost_usd being set is the permanent record
    that delivery was applied; get_portfolio_cash_and_pnl uses it to route the
    trade into the correct cash and P&L buckets.

    ITM determination
    -----------------
    Uses the most recent cached price (price_cache table) as the proxy for the
    underlying price at expiry. Falls back to the holding's avg_cost_usd if no
    cached price exists. If neither is available the option is marked EXPIRED
    without delivery (conservative — treats it as OTM).

    Delivery rules (physical settlement assumed for all ITM contracts)
    -----------------------------------------------------------------
    SELL CALL ITM → shares called away  : SELL delivery tx at strike
    BUY  CALL ITM → exercise long call  : BUY  delivery tx at strike
    SELL PUT  ITM → shares assigned     : BUY  delivery tx at strike
    BUY  PUT  ITM → exercise long put   : SELL delivery tx at strike
    """
    from app.services.transaction_service import recalculate_holding

    expired_open = option_repo.get_expired_open(db)
    details: list[ExpiredOptionResult] = []
    today_str = date.today().isoformat()

    for trade in expired_open:
        asset = trade.underlying_asset
        shares = trade.quantity * 100

        # --- ITM determination ---
        cached = price_cache_repo.get_by_symbol(db, asset.symbol)
        if cached is not None:
            underlying_price: float | None = cached.price_usd
        else:
            current_holding = holding_repo.get_by_asset_id(db, asset.id)
            underlying_price = current_holding.avg_cost_usd if current_holding else None

        itm = False
        if underlying_price is not None:
            itm = underlying_price > trade.strike if trade.option_type == "CALL" \
                else underlying_price < trade.strike

        # --- Mark EXPIRED (idempotency guard) ---
        trade.status = "EXPIRED"
        trade.exit_date = today_str
        trade.exit_price = 0.0
        trade.net_pnl = calculate_option_pnl(trade)

        delivery_cash = 0.0

        if itm:
            # Capture avg_cost BEFORE the delivery transaction changes the holding.
            # This is the only point in time we know the cost basis of the shares
            # being delivered; store it on the trade for permanent audit.
            holding_before = holding_repo.get_by_asset_id(db, asset.id)
            avg_cost_at_delivery = holding_before.avg_cost_usd if holding_before else trade.strike
            trade.delivery_avg_cost_usd = avg_cost_at_delivery

            # Map to delivery transaction type
            if trade.action == "SELL" and trade.option_type == "CALL":
                tx_type, cash_sign = "SELL", +1
            elif trade.action == "BUY" and trade.option_type == "CALL":
                tx_type, cash_sign = "BUY", -1
            elif trade.action == "SELL" and trade.option_type == "PUT":
                tx_type, cash_sign = "BUY", -1
            else:  # BUY PUT
                tx_type, cash_sign = "SELL", +1

            delivery_cash = cash_sign * trade.strike * shares

            transaction_repo.create(
                db,
                asset_id=asset.id,
                type=tx_type,
                quantity=float(shares),
                price_per_share=trade.strike,
                price_usd=trade.strike,
                fx_rate_to_usd=1.0,
                trade_date=today_str,
                notes=(
                    f"Option delivery: {trade.action} {trade.option_type} "
                    f"x{trade.quantity} @ {trade.strike} exp {trade.expiration_date}"
                ),
                source="option_delivery",
            )
            recalculate_holding(db, asset.id)

        db.flush()

        option_pnl = calculate_option_pnl(trade)

        details.append(ExpiredOptionResult(
            option_id=trade.id,
            symbol=asset.symbol,
            option_type=trade.option_type,
            action=trade.action,
            strike=trade.strike,
            expiration_date=str(trade.expiration_date),
            quantity=trade.quantity,
            itm=itm,
            shares_delivered=shares if itm else 0,
            cash_delta=option_pnl + delivery_cash,
        ))

    realized = get_portfolio_cash_and_pnl(db)
    return ProcessExpiredResult(
        processed=len(details),
        details=details,
        cash_balance=realized.total_cash,
    )
