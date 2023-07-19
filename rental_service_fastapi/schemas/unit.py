from pydantic import BaseModel

class UnitBase(BaseModel):
    unit_name: str
    unit_to_seconds: int

class Unit(UnitBase):
    id: int

    class Config:
        orm_mode = True