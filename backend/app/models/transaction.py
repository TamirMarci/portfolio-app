import uuid
from sqlalchemy import Boolean, Column, String, Float, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        # Natural deduplication key: same asset, type, date, quantity, and price = same trade
        UniqueConstraint("asset_id", "type", "trade_date", "quantity", "price_per_share", name="uq_transaction_natural_key"),
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_id = Column(String, ForeignKey("assets.id"), nullable=False)

    # BUY or SELL
    type = Column(String(4), nullable=False)

    quantity = Column(Float, nullable=False)

    # Price in the asset's native currency at time of trade
    price_per_share = Column(Float, nullable=False)

    # Price converted to USD at time of trade (None if not available)
    price_usd = Column(Float)

    # FX rate used to convert native price → USD (1.0 for USD assets)
    fx_rate_to_usd = Column(Float)

    # ISO date string: YYYY-MM-DD
    trade_date = Column(String(10), nullable=False)

    fees = Column(Float, default=0.0)
    notes = Column(Text)

    # Bootstrap/seed fields
    is_bootstrap = Column(Boolean, default=False, nullable=False)
    source = Column(String, nullable=True)

    asset = relationship("Asset", back_populates="transactions")
