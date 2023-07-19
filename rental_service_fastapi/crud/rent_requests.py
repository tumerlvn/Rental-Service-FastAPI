from sqlalchemy.orm import Session
from ..auth import auth_helper as at
from datetime import datetime
import decimal
from typing import Annotated
from fastapi import Depends

from .. import models, schemas
from ..utils import SkipLimit
from ..enum import RequestApprovedState

def get_rent_request(db: Session, rent_request_id: int):
    return db.query(models.RentRequest).filter(models.RentRequest.id == rent_request_id).first()

def get_rent_requests_to_me(db: Session, user: schemas.User, sl: SkipLimit):
    # может быть неправильный join
    return db.query(models.RentRequest).join(models.Item).join(models.User)\
        .filter(models.Item.owner_id==models.User.id)\
        .filter(models.User.id==user.id)\
        .offset(sl.skip).limit(sl.limit).all()

def get_rent_requests_to_me_not_expired(db: Session, user: schemas.User, sl: SkipLimit):
    # может быть неправильный join
    # Todo: исправить эту хрень: не выводит все реквесты на айтем
    return db.query(models.RentRequest).join(models.Item).join(models.User)\
        .filter(models.Item.owner_id==models.User.id)\
        .filter(models.User.id==user.id)\
        .filter(models.RentRequest.time_to > datetime.now())\
        .offset(sl.skip).limit(sl.limit).all()

def get_rent_requests_mine(db: Session, user: schemas.User, sl: SkipLimit):
    return db.query(models.RentRequest).filter(models.RentRequest.renter_id == user.id)\
        .offset(sl.skip).limit(sl.limit).all()

def get_rent_requests_mine_not_expired(db: Session, user: schemas.User, sl: SkipLimit):
    return db.query(models.RentRequest)\
        .filter(models.RentRequest.renter_id == user.id)\
        .filter(models.RentRequest.time_to > datetime.now())\
        .offset(sl.skip).limit(sl.limit).all()

def get_owner_of_item_requested(db: Session, rent_request: schemas.RentRequest):
    return db.query(models.User)\
        .join(models.Item)\
        .join(models.RentRequest)\
        .filter(models.User.id == models.Item.owner_id)\
        .filter(models.RentRequest.id == rent_request.id)\
        .first()

def post_rent_request_for_item(
    db: Session, 
    renter: schemas.User, 
    item: schemas.Item, 
    rent_request: schemas.RentRequestBase
):
    db_rent_request = models.RentRequest(
        item_id =  item.id,
        renter_id = renter.id,
        time_from = rent_request.time_from,
        time_to = rent_request.time_to
    )

    db.add(db_rent_request)
    db.commit()
    db.refresh(db_rent_request)
    return db_rent_request

def change_status_of_request(
    db: Session,
    rent_request: schemas.RentRequest,
    request_status: RequestApprovedState
):
    db_request = db.query(models.RentRequest)\
        .filter(models.RentRequest.id == rent_request.id).first()
    db_request.approved = request_status
    db.commit()
    db.refresh(db_request)
    delete_rent_requests_time_intersected(db, db_request)
    return db_request

def delete_rent_request(db: Session, rent_request: schemas.RentRequest):
    db.query(models.RentRequest).filter(models.RentRequest.id == rent_request.id).delete()
    db.commit()

def delete_rent_requests_time_intersected(db: Session, rent_request: schemas.RentRequest):
    db.query(models.RentRequest)\
        .filter(models.RentRequest.id != rent_request.id)\
        .filter(models.RentRequest.approved != RequestApprovedState.yes)\
        .filter(
            ((models.RentRequest.time_from <= rent_request.time_to) & (models.RentRequest.time_to >= rent_request.time_from)) |
            ((models.RentRequest.time_from >= rent_request.time_from) & (models.RentRequest.time_to <= rent_request.time_to)) |
            ((models.RentRequest.time_from <= rent_request.time_from) & (models.RentRequest.time_to >= rent_request.time_from)) |
            ((models.RentRequest.time_from <= rent_request.time_to) & (models.RentRequest.time_to >= rent_request.time_to))
        ).delete()
    db.commit()
