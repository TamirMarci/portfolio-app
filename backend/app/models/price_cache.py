from sqlalchemy import Column, String, Float
from app.database import Base


class PriceCache(Base):
    """
    Stores the most recent fetched price for each symbol.
    One row per symbol — overwritten on each refresh.
    """
    __tablename__ = "price_cache"

    symbol = Column(String(20), primary_key=True)

    # Always in USD (FX-converted for non-USD assets)
    price_usd = Column(Float, nullable=False)

    # Raw price in native currency (preserved for transparency)
    price_native = Column(Float)
    native_currency = Column(String(3))

    # ISO datetime string: YYYY-MM-DDTHH:MM:SS
    fetched_at = Column(String(26), nullable=False)

    source = Column(String(50), default="yfinance")
