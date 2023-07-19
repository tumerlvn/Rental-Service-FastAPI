from pydantic import BaseModel
from datetime import datetime

# class RentBase(BaseModel):
#     time_from: datetime
#     time_to: datetime

class Rent(BaseModel):
    id: int
    item_id: int
    renter_id: int
    unit_id: int
    price_per_unit: float
    price_total: float
    time_from: datetime
    time_to: datetime

    class Config:
        orm_mode = True