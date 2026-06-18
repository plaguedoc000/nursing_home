from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.pansionat import Pansionat
from app.models.room import Room
from app.models.room_type import RoomType
from app.schemas.room import RoomCreate, RoomResponse

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("/", response_model=list[RoomResponse])
def get_all(db: Session = Depends(get_db)):
    return db.execute(select(Room)).scalars().all()


@router.get("/{room_id}", response_model=RoomResponse)
def get_one(room_id: int, db: Session = Depends(get_db)):
    room = db.get(Room, room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.post("/", response_model=RoomResponse, status_code=201)
def create(data: RoomCreate, db: Session = Depends(get_db)):
    # проверяем что пансионат и тип комнаты существуют, иначе будет 500
    if db.get(Pansionat, data.pansionat_id) is None:
        raise HTTPException(status_code=404, detail="Pansionat not found")
    if db.get(RoomType, data.room_type_id) is None:
        raise HTTPException(status_code=404, detail="Room type not found")
    room = Room(**data.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


@router.put("/{room_id}", response_model=RoomResponse)
def update(room_id: int, data: RoomCreate, db: Session = Depends(get_db)):
    room = db.get(Room, room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    # тоже проверяем FK при обновлении, не только при создании
    if db.get(Pansionat, data.pansionat_id) is None:
        raise HTTPException(status_code=404, detail="Pansionat not found")
    if db.get(RoomType, data.room_type_id) is None:
        raise HTTPException(status_code=404, detail="Room type not found")
    for field, value in data.model_dump().items():
        setattr(room, field, value)
    db.commit()
    db.refresh(room)
    return room


@router.delete("/{room_id}", status_code=204)
def delete(room_id: int, db: Session = Depends(get_db)):
    room = db.get(Room, room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    try:
        db.delete(room)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Cannot delete: room has beds")
