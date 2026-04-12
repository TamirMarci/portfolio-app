from sqlalchemy.orm import Session, joinedload
from app.models.snapshot import PortfolioSnapshot, SnapshotHolding


def get_all(db: Session) -> list[PortfolioSnapshot]:
    return db.query(PortfolioSnapshot).order_by(PortfolioSnapshot.snapshot_date.desc()).all()


def get_by_id(db: Session, snapshot_id: str) -> PortfolioSnapshot | None:
    return (
        db.query(PortfolioSnapshot)
        .options(joinedload(PortfolioSnapshot.holdings).joinedload(SnapshotHolding.asset))
        .filter(PortfolioSnapshot.id == snapshot_id)
        .first()
    )


def update_label(db: Session, snap: PortfolioSnapshot, label: str | None) -> PortfolioSnapshot:
    snap.label = label
    db.flush()
    return snap


def delete(db: Session, snap: PortfolioSnapshot) -> None:
    db.delete(snap)
    db.flush()


def get_by_date(db: Session, snapshot_date: str) -> PortfolioSnapshot | None:
    return db.query(PortfolioSnapshot).filter(PortfolioSnapshot.snapshot_date == snapshot_date).first()


def create_snapshot(
    db: Session,
    snapshot_date: str,
    label: str | None,
    total_cost_usd: float | None,
    total_value_usd: float | None,
) -> PortfolioSnapshot:
    snap = PortfolioSnapshot(
        snapshot_date=snapshot_date,
        label=label,
        total_cost_usd=total_cost_usd,
        total_value_usd=total_value_usd,
    )
    db.add(snap)
    db.flush()
    return snap


def add_holding(
    db: Session,
    snapshot_id: str,
    asset_id: str,
    quantity: float,
    avg_cost_usd: float,
    price_at_snapshot: float,
    value_usd: float,
) -> SnapshotHolding:
    sh = SnapshotHolding(
        snapshot_id=snapshot_id,
        asset_id=asset_id,
        quantity=quantity,
        avg_cost_usd=avg_cost_usd,
        price_at_snapshot=price_at_snapshot,
        value_usd=value_usd,
    )
    db.add(sh)
    db.flush()
    return sh
