from sqlalchemy.orm import Session
from ..auth import auth_helper as at
from datetime import datetime
import decimal
from typing import Annotated
from fastapi import Depends

from .. import models, schemas
from ..utils import SkipLimit

def get_item(db: Session, item_id: int):
    return db.query(models.Item).filter(models.Item.id == item_id).first()

def get_items(db: Session, sl: SkipLimit):
    return db.query(models.Item).offset(sl.skip).limit(sl.limit).all()

def get_available_items(db: Session, is_available: bool, sl: SkipLimit):
    return db.query(models.Item).filter(models.Item.available == is_available).offset(sl.skip).limit(sl.limit).all()

def get_items_by_user(db: Session, user: schemas.User, sl: SkipLimit):
    return db.query(models.Item).filter(models.Item.owner_id == user.id).offset(sl.skip).limit(sl.limit).all()

def create_item(
    db: Session,
    item: schemas.ItemBase,
    unit: schemas.Unit,
    type: schemas.ItemType,
    owner: schemas.User,
    location: schemas.Location
):
    db_item = models.Item(
        item_name = item.item_name,
        item_type_id = type.id,
        location_id = location.id,
        item_location = location.name,
        description = item.description,
        owner_id = owner.id,
        price_per_unit = item.price_per_unit,
        unit_id = unit.id,
        available = item.available
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_availability_of_item(db: Session, item: schemas.Item, is_available: bool):
    db_item = db.query(models.Item).filter(models.Item.id == item.id).first()
    db_item.available = is_available
    db.commit()
    db.refresh(db_item)
    return db_item
    

def delete_item(db: Session, item: schemas.Item):
    db.query(models.Item).filter(models.Item.id == item.id).delete()
    db.commit()
