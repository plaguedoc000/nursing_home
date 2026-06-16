from pydantic import BaseModel, ConfigDict


class PansionatCreate(BaseModel):
    name: str
    address: str


class PansionatResponse(PansionatCreate):
    pansionat_id: int

    model_config = ConfigDict(from_attributes=True)
