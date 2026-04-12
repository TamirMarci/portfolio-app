from datetime import date

from sqlalchemy.orm import Session, joinedload
from app.models.option_trade import OptionTrade
from app.models.asset import Asset


def get_by_id(db: Session, option_id: str) -> OptionTrade | None:
    return db.query(OptionTrade).filter(OptionTrade.id == option_id).first()


def update(
    db: Session,
    trade: OptionTrade,
    option_type: str,
    action: str,
    strike: float,
    expiration_date: str,
    quantity: int,
    open_date: str,
    open_price: float,
    open_commission: float = 0.0,
    exit_date: str | None = None,
    exit_price: float | None = None,
    close_commission: float = 0.0,
    status: str = "OPEN",
    net_pnl: float | None = None,
    notes: str | None = None,
) -> OptionTrade:
    trade.option_type = option_type
    trade.action = action
    trade.strike = strike
    trade.expiration_date = expiration_date
    trade.quantity = quantity
    trade.open_date = open_date
    trade.open_price = open_price
    trade.open_commission = open_commission
    trade.exit_date = exit_date
    trade.exit_price = exit_price
    trade.close_commission = close_commission
    trade.status = status
    trade.net_pnl = net_pnl
    trade.notes = notes
    db.flush()
    return trade


def delete(db: Session, trade: OptionTrade) -> None:
    db.delete(trade)
    db.flush()


def get_by_natural_key(
    db: Session,
    underlying_asset_id: str,
    option_type: str,
    action: str,
    strike: float,
    expiration_date: str,
    open_date: str,
) -> OptionTrade | None:
    return (
        db.query(OptionTrade)
        .filter(
            OptionTrade.underlying_asset_id == underlying_asset_id,
            OptionTrade.option_type == option_type,
            OptionTrade.action == action,
            OptionTrade.strike == strike,
            OptionTrade.expiration_date == expiration_date,
            OptionTrade.open_date == open_date,
        )
        .first()
    )


def get_expired_open(db: Session) -> list[OptionTrade]:
    """Return all OPEN option trades whose expiration_date is before today."""
    today = date.today().isoformat()
    return (
        db.query(OptionTrade)
        .options(joinedload(OptionTrade.underlying_asset))
        .filter(
            OptionTrade.status == "OPEN",
            OptionTrade.expiration_date < today,
        )
        .all()
    )


def get_all_with_asset(db: Session) -> list[OptionTrade]:
    return (
        db.query(OptionTrade)
        .options(joinedload(OptionTrade.underlying_asset))
        .join(Asset, OptionTrade.underlying_asset_id == Asset.id)
        .order_by(OptionTrade.open_date.desc())
        .all()
    )


def create(
    db: Session,
    underlying_asset_id: str,
    option_type: str,
    action: str,
    strike: float,
    expiration_date: str,
    quantity: int,
    open_date: str,
    open_price: float,
    open_commission: float = 0.0,
    exit_date: str | None = None,
    exit_price: float | None = None,
    close_commission: float = 0.0,
    status: str = "OPEN",
    net_pnl: float | None = None,
    notes: str | None = None,
) -> OptionTrade:
    trade = OptionTrade(
        underlying_asset_id=underlying_asset_id,
        option_type=option_type,
        action=action,
        strike=strike,
        expiration_date=expiration_date,
        quantity=quantity,
        open_date=open_date,
        open_price=open_price,
        open_commission=open_commission,
        exit_date=exit_date,
        exit_price=exit_price,
        close_commission=close_commission,
        status=status,
        net_pnl=net_pnl,
        notes=notes,
    )
    db.add(trade)
    db.flush()
    return trade
