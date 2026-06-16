import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Date, ForeignKey

from app.database import Base


class Booking(Base):
    __tablename__ = "bookings"

    booking_id: Mapped[int] = mapped_column(primary_key=True)
    bed_id: Mapped[int] = mapped_column(ForeignKey("beds.bed_id"))
    future_res_last_name: Mapped[str] = mapped_column(String(50))
    future_res_first_name: Mapped[str] = mapped_column(String(50))
    future_res_mid_name: Mapped[str] = mapped_column(String(50))
    contact_phone: Mapped[str] = mapped_column(String(20))
    planned_check_in: Mapped[datetime.date] = mapped_column(Date)
    planned_check_out: Mapped[datetime.date] = mapped_column(Date)

    bed: Mapped["Bed"] = relationship(back_populates="bookings")
