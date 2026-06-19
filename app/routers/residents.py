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
from app.schemas.resident import ResidentCheckIn, ResidentExtend, ResidentResponse, ResidentUpdate

router = APIRouter(prefix="/residents", tags=["residents"])


@router.get("/", response_model=list[ResidentResponse])
def get_all(is_current: bool | None = None, db: Session = Depends(get_db)):
    query = select(Resident)
    if is_current is not None:
        query = query.where(Resident.is_current == is_current)
    return db.execute(query).scalars().all()


@router.get("/{record_id}", response_model=ResidentResponse)
def get_one(record_id: int, db: Session = Depends(get_db)):
    resident = db.get(Resident, record_id)
    if resident is None:
        raise HTTPException(status_code=404, detail="Resident not found")
    return resident


@router.post("/check-in", response_model=ResidentResponse, status_code=201)
def check_in(data: ResidentCheckIn, db: Session = Depends(get_db)):
    bed = db.get(Bed, data.bed_id)
    if bed is None:
        raise HTTPException(status_code=404, detail="Bed not found")
    if not bed.is_active:
        raise HTTPException(status_code=400, detail="Bed is under repair")
    if bed.current_resident_id is not None:
        raise HTTPException(status_code=400, detail="Bed is already occupied")
    # if data.planned_check_out <= datetime.date.today():
    #     raise HTTPException(status_code=400, detail="Planned check-out must be in the future")
    if data.planned_check_out < datetime.date.today():
        raise HTTPException(status_code=400, detail="Planned check-out must be in the future")

    # проверяем нет ли активных броней на это место
    overlap_booking = db.execute(
        select(Booking).where(
            Booking.bed_id == data.bed_id,
            Booking.planned_check_in < data.planned_check_out,
            Booking.planned_check_out > datetime.date.today(),
        )
    ).scalar_one_or_none()
    if overlap_booking is not None:
        raise HTTPException(status_code=400, detail="Bed has an active booking for these dates")

    room = db.get(Room, bed.room_id)
    room_type = db.get(RoomType, room.room_type_id)

    resident = Resident(
        last_name=data.last_name,
        first_name=data.first_name,
        middle_name=data.middle_name,
        passport_series=data.passport_series,
        passport_number=data.passport_number,
        birth_date=data.birth_date,
        check_in_date=datetime.date.today(),
        planned_check_out=data.planned_check_out,
        # цена фиксируется на момент заселения, не меняется при изменении тарифа
        check_in_price=room_type.base_price,
        is_current=True,
    )
    db.add(resident)
    try:
        # flush чтобы получить record_id до commit
        db.flush()
        bed.current_resident_id = resident.record_id
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Bed was just occupied by someone else")
    db.refresh(resident)
    return resident


@router.put("/{record_id}", response_model=ResidentResponse)
def update(record_id: int, data: ResidentUpdate, db: Session = Depends(get_db)):
    resident = db.get(Resident, record_id)
    if resident is None:
        raise HTTPException(status_code=404, detail="Resident not found")
    if not resident.is_current:
        raise HTTPException(status_code=400, detail="Resident has already checked out")
    for field, value in data.model_dump().items():
        setattr(resident, field, value)
    db.commit()
    db.refresh(resident)
    return resident


@router.patch("/{record_id}/extend", response_model=ResidentResponse)
def extend_stay(record_id: int, data: ResidentExtend, db: Session = Depends(get_db)):
    resident = db.get(Resident, record_id)
    if resident is None:
        raise HTTPException(status_code=404, detail="Resident not found")
    if not resident.is_current:
        raise HTTPException(status_code=400, detail="Resident has already checked out")
    if data.planned_check_out <= datetime.date.today():
        raise HTTPException(status_code=400, detail="New check-out date must be in the future")
    resident.planned_check_out = data.planned_check_out
    db.commit()
    db.refresh(resident)
    return resident


# TODO: может стоит хранить bed_id прямо в таблице residents?
# сейчас при checkout ищем кровать обратным запросом по current_resident_id
@router.post("/{record_id}/check-out", response_model=ResidentResponse)
def check_out(record_id: int, db: Session = Depends(get_db)):
    resident = db.get(Resident, record_id)
    if resident is None:
        raise HTTPException(status_code=404, detail="Resident not found")
    if not resident.is_current:
        raise HTTPException(status_code=400, detail="Resident has already checked out")

    resident.is_current = False
    resident.actual_check_out = datetime.date.today()

    # ищем кровать по жильцу и освобождаем
    bed = db.execute(
        select(Bed).where(Bed.current_resident_id == record_id)
    ).scalar_one_or_none()
    if bed is not None:
        bed.current_resident_id = None

    db.commit()
    db.refresh(resident)
    return resident
