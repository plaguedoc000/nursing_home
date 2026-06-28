import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.bed import Bed
from app.models.booking import Booking
from app.models.resident import Resident
from app.models.room import Room
from app.models.room_type import RoomType
from app.schemas.booking import (
    BookingCheckIn,
    BookingCreate,
    BookingUpdate,
    BookingResponse,
)
from app.schemas.resident import ResidentResponse

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
        raise HTTPException(
            status_code=400, detail="Check-in date must be before check-out date"
        )

    bed = db.get(Bed, data.bed_id)
    if bed is None:
        raise HTTPException(status_code=404, detail="Bed not found")

    # overlap = db.execute(
    #     select(Booking).where(Booking.bed_id == data.bed_id)
    # ).scalar_one_or_none()
    # условие overlap: start_a < end_b AND end_a > start_b
    overlap = db.execute(
        select(Booking).where(
            Booking.bed_id == data.bed_id,
            Booking.planned_check_in < data.planned_check_out,
            Booking.planned_check_out > data.planned_check_in,
        )
    ).scalar_one_or_none()
    if overlap is not None:
        raise HTTPException(
            status_code=400, detail="Bed is already booked for these dates"
        )

    if bed.current_resident_id is not None:
        resident = db.get(Resident, bed.current_resident_id)
        if resident.is_current:
            effective_checkout = resident.actual_check_out or resident.planned_check_out
            if (
                data.planned_check_in < effective_checkout
                and data.planned_check_out > resident.check_in_date
            ):
                raise HTTPException(
                    status_code=400, detail="Bed is occupied during these dates"
                )

    booking = Booking(**data.model_dump())
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.put("/{booking_id}", response_model=BookingResponse)
def update(booking_id: int, data: BookingUpdate, db: Session = Depends(get_db)):
    booking = db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    if data.planned_check_in >= data.planned_check_out:
        raise HTTPException(
            status_code=400, detail="Check-in date must be before check-out date"
        )
    overlap = db.execute(
        select(Booking).where(
            Booking.bed_id == booking.bed_id,
            Booking.booking_id != booking_id,
            Booking.planned_check_in < data.planned_check_out,
            Booking.planned_check_out > data.planned_check_in,
        )
    ).scalar_one_or_none()
    if overlap is not None:
        raise HTTPException(
            status_code=400, detail="Bed is already booked for these dates"
        )
    for field, value in data.model_dump().items():
        setattr(booking, field, value)
    db.commit()
    db.refresh(booking)
    return booking


@router.post("/{booking_id}/check-in", response_model=ResidentResponse, status_code=201)
def check_in_from_booking(
    booking_id: int, data: BookingCheckIn, db: Session = Depends(get_db)
):
    booking = db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")

    bed = db.get(Bed, booking.bed_id)
    if bed is None:
        raise HTTPException(status_code=404, detail="Bed not found")
    if not bed.is_active:
        raise HTTPException(status_code=400, detail="Bed is under repair")
    if bed.current_resident_id is not None:
        raise HTTPException(status_code=400, detail="Bed is already occupied")

    room = db.get(Room, bed.room_id)
    room_type = db.get(RoomType, room.room_type_id)

    resident = Resident(
        last_name=booking.future_res_last_name,
        first_name=booking.future_res_first_name,
        middle_name=booking.future_res_mid_name,
        passport_series=data.passport_series,
        passport_number=data.passport_number,
        birth_date=data.birth_date,
        check_in_date=datetime.date.today(),
        planned_check_out=booking.planned_check_out,
        check_in_price=room_type.base_price,
        is_current=True,
    )
    db.add(resident)
    try:
        db.flush()
        bed.current_resident_id = resident.record_id
        db.delete(booking)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="Bed was just occupied by someone else"
        )
    db.refresh(resident)
    return resident


@router.delete("/{booking_id}", status_code=204)
def delete(booking_id: int, db: Session = Depends(get_db)):
    booking = db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    db.delete(booking)
    db.commit()
