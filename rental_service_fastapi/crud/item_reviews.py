from sqlalchemy.orm import Session
from sqlalchemy import sql
from ..auth import auth_helper as at
from datetime import datetime
import decimal
from typing import Annotated
from fastapi import Depends

from .. import models, schemas
from ..utils import SkipLimit

def get_item_review(db: Session, item_review_id: int):
    return db.query(models.ItemReview).filter(models.ItemReview.id == item_review_id).first()

def get_item_review_by_reviewer_and_item_ids(db: Session, reviewer_id: int, item_id: int):
    return db.query(models.ItemReview).filter(models.ItemReview.reviewer_id == reviewer_id)\
        .filter(models.ItemReview.rented_item_id == item_id).first()

def get_item_reviews_by_item_id(db: Session, item_id: int, sl: SkipLimit):
    return db.query(models.ItemReview).filter(models.ItemReview.rented_item_id == item_id)\
        .offset(sl.skip).limit(sl.limit).all()

def get_item_reviews_by_reviewer_id(db: Session, reviewer_id: int, sl: SkipLimit):
    return db.query(models.ItemReview).filter(models.ItemReview.reviewer_id == reviewer_id)\
        .offset(sl.skip).limit(sl.limit).all()

def get_item_reviews_by_owner_id(db: Session, owner_id: int, sl: SkipLimit):
    return db.query(models.ItemReview).join(models.Item).join(models.User)\
        .filter(models.User.id == owner_id).offset(sl.skip).limit(sl.limit).all()

def get_item_grade(db: Session, item_id: int):
    return db.query(sql.func.avg(models.ItemReview.grade))\
        .filter(models.ItemReview.rented_item_id == item_id)

def create_item_review(
    db: Session, 
    item_review_base: schemas.ItemReviewBase, 
    reviewer: schemas.User, 
    item: schemas.Item
):
    db_item_review = models.ItemReview(
        rented_item_id = item.id,
        reviewer_id = reviewer.id,
        grade = item_review_base.grade,
        description = item_review_base.description,
        date = item_review_base.date,
    )
    db.add(db_item_review)
    db.commit()
    db.refresh(db_item_review)
    return db_item_review
    
def delete_item_review(
    db: Session,
    item_review_id: int
):
    db.query(models.ItemReview).filter(models.ItemReview.id == item_review_id).delete()
    db.commit()

# Todo: надо проверить как будет проходить удаление(каскадно или как попало)