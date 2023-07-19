from pydantic import BaseModel
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    hashed_password: str
    location_id: int | None = None
    location_details: str | None = None
    registration_time: datetime
    role: str

    class Config:
        orm_mode = True