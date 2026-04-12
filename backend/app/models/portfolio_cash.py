from sqlalchemy import Column, String, Float
from app.database import Base


class PortfolioCash(Base):
    __tablename__ = "portfolio_cash"

    # Singleton row — always id="default"
    id = Column(String, primary_key=True, default="default")
    balance_usd = Column(Float, nullable=False, default=0.0)
