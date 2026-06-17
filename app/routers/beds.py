from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.bed import Bed
from app.models.room import Room
from app.schemas.bed import BedCreate, BedStatusUpdate, BedResponse

router = APIRouter(prefix="/beds", tags=["beds"])


@router.get("/", response_model=list[BedResponse])
def get_all(db: Session = Depends(get_db)):
    return db.execute(select(Bed)).scalars().all()


@router.get("/{bed_id}", response_model=BedResponse)
def get_one(bed_id: int, db: Session = Depends(get_db)):
    bed = db.get(Bed, bed_id)
    if bed is None:
        raise HTTPException(status_code=404, detail="Bed not found")
    return bed


@router.post("/", response_model=BedResponse, status_code=201)
def create(data: BedCreate, db: Session = Depends(get_db)):
    if db.get(Room, data.room_id) is None:
        raise HTTPException(status_code=404, detail="Room not found")
    bed = Bed(**data.model_dump())
    db.add(bed)
    db.commit()
    db.refresh(bed)
    return bed


@router.patch("/{bed_id}/status", response_model=BedResponse)
def update_status(bed_id: int, data: BedStatusUpdate, db: Session = Depends(get_db)):
    bed = db.get(Bed, bed_id)
    if bed is None:
        raise HTTPException(status_code=404, detail="Bed not found")
    if not data.is_active and bed.current_resident_id is not None:
        raise HTTPException(status_code=400, detail="Cannot deactivate bed with a current resident")
    bed.is_active = data.is_active
    db.commit()
    db.refresh(bed)
    return bed


@router.delete("/{bed_id}", status_code=204)
def delete(bed_id: int, db: Session = Depends(get_db)):
    bed = db.get(Bed, bed_id)
    if bed is None:
        raise HTTPException(status_code=404, detail="Bed not found")
    try:
        db.delete(bed)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Cannot delete: bed has bookings or a resident")
