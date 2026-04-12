import uuid
from sqlalchemy import Column, String, Float, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    # ISO date YYYY-MM-DD — e.g. 2025-12-31 for Snapshot_2025
    snapshot_date = Column(String(10), unique=True, nullable=False)
    # Human label — e.g. "EOY 2025", auto-derived from sheet name
    label = Column(String(100))
    total_cost_usd = Column(Float)
    total_value_usd = Column(Float)
    notes = Column(Text)

    holdings = relationship("SnapshotHolding", back_populates="snapshot", cascade="all, delete-orphan")


class SnapshotHolding(Base):
    __tablename__ = "snapshot_holdings"
    __table_args__ = (
        # One holding per asset per snapshot
        UniqueConstraint("snapshot_id", "asset_id", name="uq_snapshot_holding"),
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    snapshot_id = Column(String, ForeignKey("portfolio_snapshots.id"), nullable=False)
    asset_id = Column(String, ForeignKey("assets.id"), nullable=False)

    quantity = Column(Float, nullable=False)
    avg_cost_usd = Column(Float, nullable=False)

    # Stored price at snapshot time — this is a historical fact, never recomputed
    price_at_snapshot = Column(Float, nullable=False)
    value_usd = Column(Float, nullable=False)

    snapshot = relationship("PortfolioSnapshot", back_populates="holdings")
    asset = relationship("Asset", back_populates="snapshot_holdings")
