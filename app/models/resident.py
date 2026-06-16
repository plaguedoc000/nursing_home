import datetime
from decimal import Decimal

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Date, Numeric

from app.database import Base


class Resident(Base):
    __tablename__ = "residents"

    record_id: Mapped[int] = mapped_column(primary_key=True)
    last_name: Mapped[str] = mapped_column(String(50))
    first_name: Mapped[str] = mapped_column(String(50))
    middle_name: Mapped[str] = mapped_column(String(50))
    passport_series: Mapped[str] = mapped_column(String(10))
    passport_number: Mapped[str] = mapped_column(String(10))
    birth_date: Mapped[datetime.date] = mapped_column(Date)
    check_in_date: Mapped[datetime.date] = mapped_column(Date)
    planned_check_out: Mapped[datetime.date] = mapped_column(Date)
    actual_check_out: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    check_in_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    is_current: Mapped[bool] = mapped_column(default=True)
