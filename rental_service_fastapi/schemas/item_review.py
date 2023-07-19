from pydantic import BaseModel
from datetime import datetime
from ..enum import Grade

class ItemReviewBase(BaseModel):
    grade: Grade
    description: str
    date: datetime

class ItemReview(ItemReviewBase):
    id: int
    rented_item_id: int
    reviewer_id: int

    class Config:
        orm_mode = True

class AvgGradeAndReviews(BaseModel):
    avg_grade: float
    item_reviews: list[ItemReview]