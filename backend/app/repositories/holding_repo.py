from sqlalchemy.orm import Session, joinedload
from app.models.holding import Holding
from app.models.asset import Asset


def get_all_with_asset(db: Session) -> list[Holding]:
    return (
        db.query(Holding)
        .options(joinedload(Holding.asset))
        .join(Asset)
        .order_by(Asset.symbol)
        .all()
    )


def get_by_asset_id(db: Session, asset_id: str) -> Holding | None:
    return db.query(Holding).filter(Holding.asset_id == asset_id).first()


def delete(db: Session, asset_id: str) -> bool:
    """Delete the holding for the given asset. Returns True if a row was deleted."""
    holding = get_by_asset_id(db, asset_id)
    if holding:
        db.delete(holding)
        db.flush()
        return True
    return False


def delete_all(db: Session) -> int:
    """Delete all holdings. Returns the number of rows deleted."""
    count = db.query(Holding).delete()
    db.flush()
    return count


def upsert(
    db: Session,
    asset_id: str,
    quantity: float,
    avg_cost_usd: float,
    avg_cost_native: float | None = None,
    notes: str | None = None,
) -> Holding:
    holding = get_by_asset_id(db, asset_id)
    if holding:
        holding.quantity = quantity
        holding.avg_cost_usd = avg_cost_usd
        holding.avg_cost_native = avg_cost_native
        holding.notes = notes
    else:
        holding = Holding(
            asset_id=asset_id,
            quantity=quantity,
            avg_cost_usd=avg_cost_usd,
            avg_cost_native=avg_cost_native,
            notes=notes,
        )
        db.add(holding)
    db.flush()
    return holding
