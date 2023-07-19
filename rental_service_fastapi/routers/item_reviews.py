from fastapi import APIRouter, Depends, HTTPException, Request, Form, Body, Path, status, Query
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.security import OAuth2PasswordRequestForm

from .. import schemas, crud
from ..database import get_db
from ..auth import auth_helper as at
from ..utils import SkipLimit

# один человек может оставить только ноль или один отзыв для каждого предмета
# человек может оставить отзыв только для тех предметов которые он успешно арендовал

router = APIRouter(
    prefix="/item-reviews",
    tags=["item-reviews"]
)

@router.get("/item/{item_id}/", response_model=schemas.AvgGradeAndReviews)
async def read_reviews_of_item(
    current_user: Annotated[schemas.User, Depends(at.get_current_active_user)],
    item_id: Annotated[int, Path()],
    sl: SkipLimit,
    db: Session = Depends(get_db),
):
    db_item = crud.get_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db_avg_grade = crud.get_item_grade(db, item_id, sl)
    db_item_reviews = crud.get_item_reviews_by_item_id(db, item_id, sl)
    return schemas.AvgGradeAndReviews(
        avg_grade = db_avg_grade,
        item_reviews = db_item_reviews
    )

@router.get("/user/{reviewer_id}/", response_model=list[schemas.ItemReview])
async def read_reviews_of_user(
    current_user: Annotated[schemas.User, Depends(at.get_current_active_user)],
    reviewer_id: Annotated[int, Path()],
    sl: SkipLimit,
    db: Session = Depends(get_db),
):
    db_reviewer = crud.get_user(db, reviewer_id)
    if not db_reviewer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return crud.get_item_reviews_by_reviewer_id(db, reviewer_id, sl)

@router.post("/item/{item_id}/")
def review_item(
    current_user: Annotated[schemas.User, Depends(at.get_current_active_user)],
    item_review_base: Annotated[schemas.ItemReviewBase, Body()],
    item_id: Annotated[int, Path()],
    db: Session = Depends(get_db)
):
    db_item = crud.get_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db_item_review = crud.get_item_review_by_reviewer_and_item_ids(db, current_user.id, item_id)
    if db_item_review:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You already reviewed the item")
    return crud.create_item_review(db, item_review_base, current_user, db_item)

@router.delete("/{item_review_id}/")
def delete_review_item(
    current_user: Annotated[schemas.User, Depends(at.get_current_active_user)],
    item_review_id: Annotated[int, Path()],
    db: Session = Depends(get_db)
):
    db_item_review = crud.get_item_review(db, item_review_id)
    if db_item_review:
        if db_item_review.reviewer_id == current_user.id:
            crud.delete_item_review(db, item_review_id)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)