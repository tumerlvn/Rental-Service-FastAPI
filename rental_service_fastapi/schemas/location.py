from pydantic import BaseModel

class LocationBase(BaseModel):
    postal_code: str
    name: str
    description: str

class Location(LocationBase):
    id: int
    country_id: int

    class Config:
        orm_mode = True