from sqlalchemy.orm import Session
from app.models.portfolio_cash import PortfolioCash

_DEFAULT_ID = "default"


def get(db: Session) -> float:
    """Return current cash balance in USD. Returns 0.0 if not yet initialised."""
    row = db.query(PortfolioCash).filter(PortfolioCash.id == _DEFAULT_ID).first()
    return row.balance_usd if row else 0.0


def add(db: Session, amount: float) -> float:
    """Add (or subtract) amount to the cash balance. Returns the new balance."""
    row = db.query(PortfolioCash).filter(PortfolioCash.id == _DEFAULT_ID).first()
    if row:
        row.balance_usd += amount
    else:
        row = PortfolioCash(id=_DEFAULT_ID, balance_usd=amount)
        db.add(row)
    db.flush()
    return row.balance_usd
