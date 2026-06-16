from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey

from app.database import Base


class Bed(Base):
    __tablename__ = "beds"

    bed_id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.room_id"))
    bed_label: Mapped[str] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(default=True)
    current_resident_id: Mapped[int | None] = mapped_column(
        ForeignKey("residents.record_id"), unique=True, nullable=True
    )

    room: Mapped["Room"] = relationship(back_populates="beds")
    current_resident: Mapped[Optional["Resident"]] = relationship(
        foreign_keys=[current_resident_id]
    )
    bookings: Mapped[list["Booking"]] = relationship(back_populates="bed")
