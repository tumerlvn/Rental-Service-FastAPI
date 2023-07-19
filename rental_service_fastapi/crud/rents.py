from sqlalchemy.orm import Session
from ..auth import auth_helper as at
from datetime import datetime
import decimal
from typing import Annotated
from fastapi import Depends

from .. import models, schemas
from ..utils import SkipLimit

def get_rent(db: Session, rent_id: int):
    return db.query(models.Rent).filter(models.Rent.id == rent_id).first()

def get_rent_by_item(db: Session, item: schemas.Item):
    return db.query(models.Rent).filter(models.Rent.item_id == item.id).first()

def get_owner_of_rent(db: Session, rent: schemas.Rent):
    return db.query(models.User).join(models.Item).join(models.Rent).filter(models.Rent.id == rent.id).first()

# def test_get_owner_of_rent(db: Session, rent: schemas.Rent):
#     return db.query(models.User).join(models.Item).join(models.Rent).filter(models.Rent.id == rent.id).all()

def get_rents_by_owner(db: Session, owner: schemas.User, sl: SkipLimit):
    return db.query(models.Rent).join(models.Item) \
        .filter(models.Item.owner_id == owner.id) \
        .offset(sl.skip).limit(sl.limit).all()

def get_rents_by_renter(db: Session, renter: schemas.User, sl: SkipLimit):
    return db.query(models.Rent).filter(models.Rent.renter_id == renter.id).all()

def get_expired_rents_by_owner(db: Session, owner: schemas.User, sl: SkipLimit):
    return db.query(models.Rent).join(models.Item) \
        .filter(models.Item.owner_id == owner.id) \
        .filter(models.Rent.time_to <= datetime.now()) \
        .offset(sl.skip).limit(sl.limit).all()

def create_rent(db: Session, rent_time_from: datetime, rent_time_to: datetime, item: schemas.Item, renter: schemas.User):
    # unit: schemas.Unit = get_unit(db, item.unit_id)
    # возможно можно просто поменять models.Unit на Enum
    unit: schemas.Unit = db.query(models.Unit).filter(models.Unit.id == item.unit_id).first()
    total_time_in_seconds = (rent_time_to - rent_time_from).total_seconds()
    price_total = item.price_per_unit / unit.unit_to_seconds * decimal.Decimal(total_time_in_seconds)

    db_rent = models.Rent(
        item_id = item.id,
        renter_id = renter.id,
        time_from = rent_time_from,
        time_to = rent_time_to,
        unit_id = item.unit_id,
        price_per_unit = item.price_per_unit,
        price_total = price_total
    )

    # поидее фигня какая-то, надо у Азамата спросить что делать в таком случае
    db_item = db.query(models.Item).filter(models.Item.id == item.id).first()
    db_item.available = False

    db.add(db_rent)
    db.commit()
    db.refresh(db_rent)
    return db_rent

def delete_rent(db: Session, rent: schemas.Rent):
    # db_item = get_item(db, rent.item_id)
    # db_item = 
    # db_item.available = True
    db.query(models.Rent).filter(models.Rent.id == rent.id).delete()
    db.commit()