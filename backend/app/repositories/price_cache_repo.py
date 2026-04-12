from sqlalchemy.orm import Session
from app.models.price_cache import PriceCache


def get_all(db: Session) -> list[PriceCache]:
    return db.query(PriceCache).all()


def get_by_symbol(db: Session, symbol: str) -> PriceCache | None:
    return db.query(PriceCache).filter(PriceCache.symbol == symbol).first()


def get_by_symbols(db: Session, symbols: list[str]) -> dict[str, PriceCache]:
    rows = db.query(PriceCache).filter(PriceCache.symbol.in_(symbols)).all()
    return {r.symbol: r for r in rows}


def upsert(
    db: Session,
    symbol: str,
    price_usd: float,
    fetched_at: str,
    price_native: float | None = None,
    native_currency: str | None = None,
    source: str = "yfinance",
) -> PriceCache:
    entry = get_by_symbol(db, symbol)
    if entry:
        entry.price_usd = price_usd
        entry.price_native = price_native
        entry.native_currency = native_currency
        entry.fetched_at = fetched_at
        entry.source = source
    else:
        entry = PriceCache(
            symbol=symbol,
            price_usd=price_usd,
            price_native=price_native,
            native_currency=native_currency,
            fetched_at=fetched_at,
            source=source,
        )
        db.add(entry)
    db.flush()
    return entry
