"""
Transaction service — business logic for creating/updating/deleting transactions.

Holdings are recalculated from transactions after every mutation (issues 7 + 8).
Weighted average cost policy:
  - avg_cost is derived from BUY transactions only
  - SELL transactions reduce quantity but do not affect avg_cost
  - If net quantity <= 0 after a mutation, the holding is deleted
"""

from sqlalchemy.orm import Session

from app.repositories import transaction_repo, holding_repo
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionRead, TransactionList
from app.services import market_data_service


# ─── Recalculation engine ─────────────────────────────────────────────────────

def recalculate_holding(db: Session, asset_id: str) -> None:
    """
    Recalculate and upsert/delete the Holding for asset_id from all its transactions.

    Weighted average cost (issue 8):
      avg_cost = total_buy_cost / total_buy_qty
      Sells reduce quantity only; they do not change avg_cost.

    FX-aware (issue 9):
      avg_cost_native uses price_per_share (native currency)
      avg_cost_usd uses price_usd (FX-converted at time of trade), falling back to
      price_per_share when price_usd is absent (USD assets or legacy import rows).

    If net quantity <= 0, the holding row is deleted (issue 7).
    """
    transactions = transaction_repo.get_all_for_asset(db, asset_id)

    total_buy_qty = 0.0
    total_buy_cost_native = 0.0
    total_buy_cost_usd = 0.0
    total_sell_qty = 0.0

    for tx in transactions:
        if tx.type == "BUY":
            total_buy_qty += tx.quantity
            total_buy_cost_native += tx.quantity * tx.price_per_share
            usd_price = tx.price_usd if tx.price_usd is not None else tx.price_per_share
            total_buy_cost_usd += tx.quantity * usd_price
        elif tx.type == "SELL":
            total_sell_qty += tx.quantity

    net_qty = total_buy_qty - total_sell_qty

    if net_qty <= 0 or total_buy_qty == 0:
        holding_repo.delete(db, asset_id)
        return

    avg_cost_native = total_buy_cost_native / total_buy_qty
    avg_cost_usd = total_buy_cost_usd / total_buy_qty

    holding_repo.upsert(
        db,
        asset_id=asset_id,
        quantity=net_qty,
        avg_cost_usd=avg_cost_usd,
        avg_cost_native=avg_cost_native,
    )


def recalculate_all_holdings(db: Session) -> None:
    """Recalculate holdings for every asset that has at least one transaction."""
    asset_ids = transaction_repo.get_distinct_asset_ids(db)
    for asset_id in asset_ids:
        recalculate_holding(db, asset_id)


def rebuild_holdings(db: Session) -> dict:
    """
    Clear and rebuild the entire holdings table from transaction history (issue 12).

    Steps:
      1. Delete all existing holding rows.
      2. Recalculate every holding from transactions (weighted avg cost).
      3. Run integrity checks: no negative quantities, quantities match transaction totals.

    Returns a summary dict with counts and any integrity errors found.
    """
    deleted = holding_repo.delete_all(db)

    recalculate_all_holdings(db)

    holdings = holding_repo.get_all_with_asset(db)

    errors: list[str] = []
    for h in holdings:
        if h.quantity <= 0:
            errors.append(f"{h.asset.symbol}: non-positive quantity {h.quantity:.6f}")

        txs = transaction_repo.get_all_for_asset(db, h.asset_id)
        buy_qty = sum(tx.quantity for tx in txs if tx.type == "BUY")
        sell_qty = sum(tx.quantity for tx in txs if tx.type == "SELL")
        expected = buy_qty - sell_qty
        if abs(expected - h.quantity) > 1e-6:
            errors.append(
                f"{h.asset.symbol}: quantity mismatch — transactions give {expected:.6f}, holding has {h.quantity:.6f}"
            )

    return {
        "cleared": deleted,
        "rebuilt": len(holdings),
        "errors": errors,
        "valid": len(errors) == 0,
    }


# ─── CRUD operations ──────────────────────────────────────────────────────────

def _build_read(tx, asset) -> TransactionRead:
    return TransactionRead(
        id=tx.id,
        symbol=asset.symbol,
        name=asset.name,
        asset_type=asset.asset_type,
        type=tx.type,
        quantity=tx.quantity,
        price_per_share=tx.price_per_share,
        price_usd=tx.price_usd,
        fx_rate_to_usd=tx.fx_rate_to_usd,
        trade_date=str(tx.trade_date),
        fees=tx.fees or 0.0,
        notes=tx.notes,
        is_bootstrap=tx.is_bootstrap,
        source=tx.source,
        realized_pnl_usd=None,
        realized_pnl_pct=None,
    )


def create_transaction(db: Session, body: TransactionCreate) -> TransactionRead:
    """
    Resolve asset by symbol, fetch live FX rate for non-USD assets (issue 9),
    insert a new transaction, and recalculate the holding (issues 7 + 8).
    Raises ValueError if the symbol cannot be resolved.
    """
    asset = market_data_service.get_or_create_asset(db, body.symbol)

    fx_rate_to_usd = market_data_service.get_fx_rate(asset.currency)
    price_usd = body.price_usd if body.price_usd is not None else body.price_per_share * fx_rate_to_usd

    tx = transaction_repo.create(
        db,
        asset_id=asset.id,
        type=body.type,
        quantity=body.quantity,
        price_per_share=body.price_per_share,
        price_usd=price_usd,
        fx_rate_to_usd=fx_rate_to_usd,
        trade_date=body.trade_date,
        fees=body.fees,
        notes=body.notes,
    )

    recalculate_holding(db, asset.id)

    return _build_read(tx, asset)


def update_transaction(db: Session, transaction_id: str, body: TransactionUpdate) -> TransactionRead:
    """
    Update an existing transaction's fields (symbol/asset is not changeable).
    Re-fetches FX rate for non-USD assets and recalculates the holding.
    Raises ValueError if the transaction does not exist or is a bootstrap seed.
    """
    tx = transaction_repo.get_by_id(db, transaction_id)
    if tx is None:
        raise ValueError(f"Transaction not found: {transaction_id}")
    if tx.is_bootstrap:
        raise ValueError("Bootstrap seed transactions cannot be edited.")

    asset = tx.asset
    fx_rate_to_usd = market_data_service.get_fx_rate(asset.currency)
    price_usd = body.price_usd if body.price_usd is not None else body.price_per_share * fx_rate_to_usd

    tx = transaction_repo.update(
        db,
        tx,
        type=body.type,
        quantity=body.quantity,
        price_per_share=body.price_per_share,
        price_usd=price_usd,
        fx_rate_to_usd=fx_rate_to_usd,
        trade_date=body.trade_date,
        fees=body.fees,
        notes=body.notes,
    )

    recalculate_holding(db, asset.id)

    return _build_read(tx, asset)


def delete_transaction(db: Session, transaction_id: str) -> None:
    """
    Delete a transaction by ID and recalculate the holding.
    Raises ValueError if the transaction does not exist or is a bootstrap seed.
    """
    tx = transaction_repo.get_by_id(db, transaction_id)
    if tx is None:
        raise ValueError(f"Transaction not found: {transaction_id}")
    if tx.is_bootstrap:
        raise ValueError("Bootstrap seed transactions cannot be deleted.")

    asset_id = tx.asset_id
    transaction_repo.delete(db, tx)
    recalculate_holding(db, asset_id)


def get_all_transactions(db: Session) -> TransactionList:
    """Return all transactions enriched with asset metadata."""
    transactions = transaction_repo.get_all_with_asset(db)
    result = [_build_read(tx, tx.asset) for tx in transactions]
    return TransactionList(transactions=result, total_count=len(result))
