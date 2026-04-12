from sqlalchemy.orm import Session
from app.models.asset import Asset


def get_all(db: Session) -> list[Asset]:
    return db.query(Asset).order_by(Asset.symbol).all()


def get_by_symbol(db: Session, symbol: str) -> Asset | None:
    return db.query(Asset).filter(Asset.symbol == symbol).first()


def get_by_id(db: Session, asset_id: str) -> Asset | None:
    return db.query(Asset).filter(Asset.id == asset_id).first()


def upsert(db: Session, symbol: str, name: str, asset_type: str, exchange: str | None, currency: str) -> Asset:
    asset = get_by_symbol(db, symbol)
    if asset:
        asset.name = name
        asset.asset_type = asset_type
        asset.exchange = exchange
        asset.currency = currency
    else:
        asset = Asset(symbol=symbol, name=name, asset_type=asset_type, exchange=exchange, currency=currency)
        db.add(asset)
    db.flush()
    return asset
