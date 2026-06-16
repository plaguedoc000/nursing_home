from decimal import Decimal

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Numeric

from app.database import Base


class RoomType(Base):
    __tablename__ = "room_types"

    room_type_id: Mapped[int] = mapped_column(primary_key=True)
    type_name: Mapped[str] = mapped_column(String(50))
    base_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    rooms: Mapped[list["Room"]] = relationship(back_populates="room_type")
