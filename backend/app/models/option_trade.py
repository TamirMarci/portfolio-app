import uuid
from sqlalchemy import Column, String, Float, Integer, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class OptionTrade(Base):
    __tablename__ = "option_trades"
    __table_args__ = (
        # Natural deduplication key: same underlying, contract spec, and open date = same trade
        UniqueConstraint(
            "underlying_asset_id", "option_type", "action", "strike", "expiration_date", "open_date",
            name="uq_option_trade_natural_key",
        ),
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    underlying_asset_id = Column(String, ForeignKey("assets.id"), nullable=False)

    # CALL or PUT
    option_type = Column(String(4), nullable=False)
    # BUY or SELL (from the trader's perspective)
    action = Column(String(4), nullable=False)

    strike = Column(Float, nullable=False)

    # ISO date strings
    expiration_date = Column(String(10), nullable=False)
    open_date = Column(String(10), nullable=False)

    # Number of contracts (1 contract = 100 shares)
    quantity = Column(Integer, nullable=False)

    # Premium per share at open
    open_price = Column(Float, nullable=False)
    open_commission = Column(Float, default=0.0)

    # Populated when position is closed or expired
    exit_date = Column(String(10))
    exit_price = Column(Float)
    close_commission = Column(Float, default=0.0)

    # OPEN, CLOSED, or EXPIRED
    status = Column(String(10), nullable=False)

    # Broker-reported net P&L (stored as a fact, not recomputed)
    net_pnl = Column(Float)

    # Populated only for ITM expired options that triggered physical delivery.
    # Stores the underlying holding's avg_cost_usd at the moment of assignment,
    # so stock_realized_pnl = (strike - delivery_avg_cost_usd) × shares can be
    # computed without re-reading historical price data.
    delivery_avg_cost_usd = Column(Float, nullable=True)

    notes = Column(Text)

    underlying_asset = relationship("Asset", back_populates="option_trades")
