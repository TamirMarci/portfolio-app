from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import transaction_service
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionList, TransactionRead

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.get("", response_model=TransactionList)
def get_transactions(db: Session = Depends(get_db)):
    """Return all recorded transactions, sorted by date descending."""
    return transaction_service.get_all_transactions(db)


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(body: TransactionCreate, db: Session = Depends(get_db)):
    """Add a new transaction and recalculate the affected holding."""
    try:
        result = transaction_service.create_transaction(db, body)
        db.commit()
        return result
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))


@router.patch("/{transaction_id}", response_model=TransactionRead)
def update_transaction(transaction_id: str, body: TransactionUpdate, db: Session = Depends(get_db)):
    """Update an existing transaction. Symbol/asset cannot be changed."""
    try:
        result = transaction_service.update_transaction(db, transaction_id, body)
        db.commit()
        return result
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: str, db: Session = Depends(get_db)):
    """Delete a transaction and recalculate the affected holding."""
    try:
        transaction_service.delete_transaction(db, transaction_id)
        db.commit()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
