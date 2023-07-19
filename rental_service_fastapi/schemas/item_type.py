from pydantic import BaseModel

class ItemTypeBase(BaseModel):
    type_name: str

class ItemType(ItemTypeBase):
    id: int

    class Config:
        orm_mode = True