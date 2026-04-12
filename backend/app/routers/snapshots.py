from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import snapshot_service
from app.schemas.snapshot import (
    SnapshotCreate, SnapshotUpdate,
    SnapshotListItem, SnapshotRead, SnapshotCompareResult,
)

router = APIRouter(prefix="/api/snapshots", tags=["snapshots"])


@router.get("", response_model=list[SnapshotListItem])
def list_snapshots(db: Session = Depends(get_db)):
    return snapshot_service.get_all_snapshots(db)


@router.post("", response_model=SnapshotListItem, status_code=status.HTTP_201_CREATED)
def create_snapshot(body: SnapshotCreate, db: Session = Depends(get_db)):
    """Create a snapshot from the current portfolio holdings and cached prices."""
    try:
        result = snapshot_service.create_snapshot_from_holdings(db, body.label)
        db.commit()
        return result
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))


@router.get("/compare", response_model=SnapshotCompareResult)
def compare_snapshots(from_id: str, to_id: str, db: Session = Depends(get_db)):
    """Compare two snapshots — portfolio-level and per-asset deltas with executive summary."""
    try:
        return snapshot_service.compare_snapshots(db, from_id, to_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.patch("/{snapshot_id}", response_model=SnapshotListItem)
def rename_snapshot(snapshot_id: str, body: SnapshotUpdate, db: Session = Depends(get_db)):
    """Update the label of an existing snapshot."""
    try:
        result = snapshot_service.update_snapshot_label(db, snapshot_id, body.label)
        db.commit()
        return result
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/{snapshot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_snapshot(snapshot_id: str, db: Session = Depends(get_db)):
    """Delete a snapshot and all its holdings."""
    try:
        snapshot_service.delete_snapshot(db, snapshot_id)
        db.commit()
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/{snapshot_id}", response_model=SnapshotRead)
def get_snapshot(snapshot_id: str, db: Session = Depends(get_db)):
    snap = snapshot_service.get_snapshot_detail(db, snapshot_id)
    if not snap:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    return snap
