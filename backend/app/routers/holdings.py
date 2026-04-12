from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import portfolio_service
from app.schemas.holding import PortfolioSummary

router = APIRouter(prefix="/api/holdings", tags=["holdings"])


@router.get("", response_model=PortfolioSummary)
def get_holdings(db: Session = Depends(get_db)):
    """Return all current holdings enriched with live (cached) market prices."""
    return portfolio_service.get_portfolio_summary(db)
