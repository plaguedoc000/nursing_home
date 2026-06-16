from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from app.database import Base


class Pansionat(Base):
    __tablename__ = "pansionats"

    pansionat_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    address: Mapped[str] = mapped_column(String(200))

    rooms: Mapped[list["Room"]] = relationship(back_populates="pansionat")
