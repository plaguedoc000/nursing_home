import datetime

from pydantic import BaseModel, ConfigDict


class BookingCreate(BaseModel):
    bed_id: int
    future_res_last_name: str
    future_res_first_name: str
    future_res_mid_name: str
    contact_phone: str
    planned_check_in: datetime.date
    planned_check_out: datetime.date


class BookingResponse(BookingCreate):
    booking_id: int

    model_config = ConfigDict(from_attributes=True)
