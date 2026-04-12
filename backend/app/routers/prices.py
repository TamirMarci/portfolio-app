from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import holding_repo
from app.services import market_data_service
from app.schemas.price import RefreshResult, PriceCacheRead
from app.repositories import price_cache_repo

router = APIRouter(prefix="/api/prices", tags=["prices"])


@router.post("/refresh", response_model=RefreshResult)
def refresh_prices(db: Session = Depends(get_db)):
    """
    Manually trigger a live price refresh for all current holdings.
    Fetches from yfinance in a single batch call.
    Returns lists of successfully refreshed and failed symbols.
    """
    holdings = holding_repo.get_all_with_asset(db)
    symbols_with_currency = [(h.asset.symbol, h.asset.currency) for h in holdings]
    return market_data_service.refresh_prices(db, symbols_with_currency)


@router.get("", response_model=list[PriceCacheRead])
def get_cached_prices(db: Session = Depends(get_db)):
    """Return all currently cached prices."""
    return price_cache_repo.get_all(db)
