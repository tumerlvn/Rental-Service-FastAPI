from pydantic import BaseModel

class ItemBase(BaseModel):
    item_name: str
    description: str
    price_per_unit: float
    available: bool

class Item(ItemBase):
    id: int
    owner_id: int
    unit_id: int
    item_type_id: int
    location_id: int
    item_location: str

    class Config:
        orm_mode = True