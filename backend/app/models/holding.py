import uuid
from sqlalchemy import Column, String, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Holding(Base):
    __tablename__ = "holdings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_id = Column(String, ForeignKey("assets.id"), nullable=False, unique=True)

    quantity = Column(Float, nullable=False)

    # Stored in USD regardless of the asset's native currency.
    # For non-USD assets (e.g. OCO.V/CAD), the import layer converts using the
    # FX rate at the time of import and records the original in avg_cost_native.
    avg_cost_usd = Column(Float, nullable=False)

    # Original avg cost in the asset's native currency — preserved for audit.
    avg_cost_native = Column(Float)

    notes = Column(Text)

    asset = relationship("Asset", back_populates="holdings")
