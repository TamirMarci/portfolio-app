from sqlalchemy.orm import Session, joinedload
from app.models.transaction import Transaction
from app.models.asset import Asset


def get_by_id(db: Session, transaction_id: str) -> Transaction | None:
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()


def get_all_for_asset(db: Session, asset_id: str) -> list[Transaction]:
    """Return all transactions for a single asset, oldest first (for aggregation)."""
    return (
        db.query(Transaction)
        .filter(Transaction.asset_id == asset_id)
        .order_by(Transaction.trade_date.asc())
        .all()
    )


def update(
    db: Session,
    tx: Transaction,
    type: str,
    quantity: float,
    price_per_share: float,
    trade_date: str,
    price_usd: float | None = None,
    fx_rate_to_usd: float | None = None,
    fees: float = 0.0,
    notes: str | None = None,
) -> Transaction:
    tx.type = type
    tx.quantity = quantity
    tx.price_per_share = price_per_share
    tx.price_usd = price_usd
    tx.fx_rate_to_usd = fx_rate_to_usd
    tx.trade_date = trade_date
    tx.fees = fees
    tx.notes = notes
    db.flush()
    return tx


def delete(db: Session, tx: Transaction) -> None:
    db.delete(tx)
    db.flush()


def get_by_natural_key(
    db: Session,
    asset_id: str,
    type: str,
    trade_date: str,
    quantity: float,
    price_per_share: float,
) -> Transaction | None:
    return (
        db.query(Transaction)
        .filter(
            Transaction.asset_id == asset_id,
            Transaction.type == type,
            Transaction.trade_date == trade_date,
            Transaction.quantity == quantity,
            Transaction.price_per_share == price_per_share,
        )
        .first()
    )


def get_all_with_asset(
    db: Session,
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[Transaction]:
    q = db.query(Transaction).options(joinedload(Transaction.asset)).join(Asset)
    if start_date:
        q = q.filter(Transaction.trade_date >= start_date)
    if end_date:
        q = q.filter(Transaction.trade_date <= end_date)
    return q.order_by(Transaction.trade_date.desc()).all()


def get_by_source(db: Session, source: str) -> list[Transaction]:
    return db.query(Transaction).filter(Transaction.source == source).all()


def get_distinct_asset_ids(db: Session) -> list[str]:
    """Return all unique asset_ids that have at least one transaction."""
    return [row[0] for row in db.query(Transaction.asset_id).distinct().all()]


def create(
    db: Session,
    asset_id: str,
    type: str,
    quantity: float,
    price_per_share: float,
    trade_date: str,
    price_usd: float | None = None,
    fx_rate_to_usd: float | None = None,
    fees: float = 0.0,
    notes: str | None = None,
    is_bootstrap: bool = False,
    source: str | None = None,
) -> Transaction:
    tx = Transaction(
        asset_id=asset_id,
        type=type,
        quantity=quantity,
        price_per_share=price_per_share,
        price_usd=price_usd,
        fx_rate_to_usd=fx_rate_to_usd,
        trade_date=trade_date,
        fees=fees,
        notes=notes,
        is_bootstrap=is_bootstrap,
        source=source,
    )
    db.add(tx)
    db.flush()
    return tx
