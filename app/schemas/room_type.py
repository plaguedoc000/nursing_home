from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class RoomTypeCreate(BaseModel):
    type_name: str
    base_price: Decimal


class RoomTypeResponse(RoomTypeCreate):
    room_type_id: int

    model_config = ConfigDict(from_attributes=True)
