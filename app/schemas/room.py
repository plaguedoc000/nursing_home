from pydantic import BaseModel, ConfigDict


class RoomCreate(BaseModel):
    pansionat_id: int
    room_type_id: int
    room_number: str


class RoomResponse(RoomCreate):
    room_id: int

    model_config = ConfigDict(from_attributes=True)
