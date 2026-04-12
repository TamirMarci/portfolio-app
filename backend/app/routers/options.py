from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import option_service
from app.schemas.option import OptionTradeCreate, OptionTradeUpdate, OptionTradeRead, OptionsSummary, ProcessExpiredResult

router = APIRouter(prefix="/api/options", tags=["options"])


@router.post("/process-expired", response_model=ProcessExpiredResult)
def process_expired_options(db: Session = Depends(get_db)):
    """
    Detect expired OPEN option contracts, mark them EXPIRED, and apply
    physical delivery to holdings and cash for ITM contracts.
    Idempotent — safe to call multiple times.
    """
    result = option_service.process_expired_options(db)
    db.commit()
    return result


@router.get("", response_model=OptionsSummary)
def get_options(db: Session = Depends(get_db)):
    """Return all option trades with analytics and per-underlying P&L breakdown."""
    return option_service.get_options_summary(db)


@router.post("", response_model=OptionTradeRead, status_code=status.HTTP_201_CREATED)
def create_option_trade(body: OptionTradeCreate, db: Session = Depends(get_db)):
    """Add a new option trade."""
    try:
        result = option_service.create_option_trade(db, body)
        db.commit()
        return result
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))


@router.patch("/{option_id}", response_model=OptionTradeRead)
def update_option_trade(option_id: str, body: OptionTradeUpdate, db: Session = Depends(get_db)):
    """Update an existing option trade. Underlying symbol cannot be changed."""
    try:
        result = option_service.update_option_trade(db, option_id, body)
        db.commit()
        return result
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/{option_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_option_trade(option_id: str, db: Session = Depends(get_db)):
    """Delete an option trade by ID."""
    try:
        option_service.delete_option_trade(db, option_id)
        db.commit()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
