import uuid
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    # STOCK or ETF
    asset_type = Column(String(10), nullable=False)
    exchange = Column(String(20))
    # ISO 4217 native trading currency (e.g. USD, CAD)
    currency = Column(String(3), nullable=False, default="USD")

    holdings = relationship("Holding", back_populates="asset", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="asset", cascade="all, delete-orphan")
    option_trades = relationship("OptionTrade", back_populates="underlying_asset", cascade="all, delete-orphan")
    snapshot_holdings = relationship("SnapshotHolding", back_populates="asset")
