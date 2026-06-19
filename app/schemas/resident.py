import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


# TODO: добавить валидацию паспорта (серия - 4 цифры, номер - 6 цифр)
class ResidentCheckIn(BaseModel):
    bed_id: int
    last_name: str
    first_name: str
    middle_name: str
    passport_series: str
    passport_number: str
    birth_date: datetime.date
    planned_check_out: datetime.date


class ResidentResponse(BaseModel):
    record_id: int
    last_name: str
    first_name: str
    middle_name: str
    passport_series: str
    passport_number: str
    birth_date: datetime.date
    check_in_date: datetime.date
    planned_check_out: datetime.date
    actual_check_out: datetime.date | None
    check_in_price: Decimal
    is_current: bool

    model_config = ConfigDict(from_attributes=True)


class ResidentExtend(BaseModel):
    planned_check_out: datetime.date
