from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey

from app.database import Base


class Room(Base):
    __tablename__ = "rooms"

    room_id: Mapped[int] = mapped_column(primary_key=True)
    pansionat_id: Mapped[int] = mapped_column(ForeignKey("pansionats.pansionat_id"))
    room_type_id: Mapped[int] = mapped_column(ForeignKey("room_types.room_type_id"))
    room_number: Mapped[str] = mapped_column(String(10))

    pansionat: Mapped["Pansionat"] = relationship(back_populates="rooms")
    room_type: Mapped["RoomType"] = relationship(back_populates="rooms")
    beds: Mapped[list["Bed"]] = relationship(back_populates="room")
