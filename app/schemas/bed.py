from pydantic import BaseModel, ConfigDict


class BedCreate(BaseModel):
    room_id: int
    bed_label: str
    is_active: bool = True


class BedStatusUpdate(BaseModel):
    is_active: bool


class BedResponse(BaseModel):
    bed_id: int
    room_id: int
    bed_label: str
    is_active: bool
    current_resident_id: int | None

    model_config = ConfigDict(from_attributes=True)
