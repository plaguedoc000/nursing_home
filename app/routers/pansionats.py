from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.pansionat import Pansionat
from app.schemas.pansionat import PansionatCreate, PansionatResponse

router = APIRouter(prefix="/pansionats", tags=["pansionats"])


# TODO: добавить пагинацию когда записей станет много
@router.get("/", response_model=list[PansionatResponse])
def get_all(db: Session = Depends(get_db)):
    return db.execute(select(Pansionat)).scalars().all()


@router.get("/{pansionat_id}", response_model=PansionatResponse)
def get_one(pansionat_id: int, db: Session = Depends(get_db)):
    pansionat = db.get(Pansionat, pansionat_id)
    if pansionat is None:
        raise HTTPException(status_code=404, detail="Pansionat not found")
    return pansionat


@router.post("/", response_model=PansionatResponse, status_code=201)
def create(data: PansionatCreate, db: Session = Depends(get_db)):
    pansionat = Pansionat(**data.model_dump())
    db.add(pansionat)
    db.commit()
    db.refresh(pansionat)
    return pansionat


@router.put("/{pansionat_id}", response_model=PansionatResponse)
def update(pansionat_id: int, data: PansionatCreate, db: Session = Depends(get_db)):
    pansionat = db.get(Pansionat, pansionat_id)
    if pansionat is None:
        raise HTTPException(status_code=404, detail="Pansionat not found")
    for field, value in data.model_dump().items():
        setattr(pansionat, field, value)
    db.commit()
    db.refresh(pansionat)
    return pansionat


@router.delete("/{pansionat_id}", status_code=204)
def delete(pansionat_id: int, db: Session = Depends(get_db)):
    pansionat = db.get(Pansionat, pansionat_id)
    if pansionat is None:
        raise HTTPException(status_code=404, detail="Pansionat not found")
    try:
        db.delete(pansionat)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Cannot delete: pansionat has rooms")
