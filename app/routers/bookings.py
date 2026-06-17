from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.bed import Bed
from app.models.booking import Booking
from app.models.resident import Resident
from app.schemas.booking import BookingCreate, BookingResponse

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("/", response_model=list[BookingResponse])
def get_all(db: Session = Depends(get_db)):
    return db.execute(select(Booking)).scalars().all()


@router.get("/{booking_id}", response_model=BookingResponse)
def get_one(booking_id: int, db: Session = Depends(get_db)):
    booking = db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@router.post("/", response_model=BookingResponse, status_code=201)
def create(data: BookingCreate, db: Session = Depends(get_db)):
    if data.planned_check_in >= data.planned_check_out:
        raise HTTPException(status_code=400, detail="Check-in date must be before check-out date")

    bed = db.get(Bed, data.bed_id)
    if bed is None:
        raise HTTPException(status_code=404, detail="Bed not found")

    overlap = db.execute(
        select(Booking).where(
            Booking.bed_id == data.bed_id,
            Booking.planned_check_in < data.planned_check_out,
            Booking.planned_check_out > data.planned_check_in,
        )
    ).scalar_one_or_none()
    if overlap is not None:
        raise HTTPException(status_code=400, detail="Bed is already booked for these dates")

    if bed.current_resident_id is not None:
        resident = db.get(Resident, bed.current_resident_id)
        if (data.planned_check_in < resident.planned_check_out
                and data.planned_check_out > resident.check_in_date):
            raise HTTPException(status_code=400, detail="Bed is occupied during these dates")

    booking = Booking(**data.model_dump())
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.delete("/{booking_id}", status_code=204)
def delete(booking_id: int, db: Session = Depends(get_db)):
    booking = db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    db.delete(booking)
    db.commit()
