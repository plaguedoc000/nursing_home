from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.room_type import RoomType
from app.schemas.room_type import RoomTypeCreate, RoomTypeResponse

router = APIRouter(prefix="/room-types", tags=["room-types"])


@router.get("/", response_model=list[RoomTypeResponse])
def get_all(db: Session = Depends(get_db)):
    return db.execute(select(RoomType)).scalars().all()


@router.get("/{room_type_id}", response_model=RoomTypeResponse)
def get_one(room_type_id: int, db: Session = Depends(get_db)):
    room_type = db.get(RoomType, room_type_id)
    if room_type is None:
        raise HTTPException(status_code=404, detail="Room type not found")
    return room_type


@router.post("/", response_model=RoomTypeResponse, status_code=201)
def create(data: RoomTypeCreate, db: Session = Depends(get_db)):
    # TODO: валидировать что цена > 0 (сейчас можно передать отрицательную)
    room_type = RoomType(**data.model_dump())
    db.add(room_type)
    db.commit()
    db.refresh(room_type)
    return room_type


@router.put("/{room_type_id}", response_model=RoomTypeResponse)
def update(room_type_id: int, data: RoomTypeCreate, db: Session = Depends(get_db)):
    room_type = db.get(RoomType, room_type_id)
    if room_type is None:
        raise HTTPException(status_code=404, detail="Room type not found")
    for field, value in data.model_dump().items():
        setattr(room_type, field, value)
    db.commit()
    db.refresh(room_type)
    return room_type


@router.delete("/{room_type_id}", status_code=204)
def delete(room_type_id: int, db: Session = Depends(get_db)):
    room_type = db.get(RoomType, room_type_id)
    if room_type is None:
        raise HTTPException(status_code=404, detail="Room type not found")
    try:
        db.delete(room_type)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Cannot delete: room type is used in rooms")
