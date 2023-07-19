from pydantic import BaseModel
from datetime import datetime
from ..enum import RequestApprovedState

class RentRequestBase(BaseModel):
    time_from: datetime
    time_to: datetime

class RentRequest(RentRequestBase):
    id: int
    approved: RequestApprovedState = RequestApprovedState.not_yet
    item_id: int
    renter_id: int

    class Config:
        orm_mode = True