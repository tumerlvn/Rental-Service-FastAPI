from sqlalchemy.orm import Session
from .auth import auth_helper as at
from datetime import datetime
import decimal
from typing import Annotated
from fastapi import Depends

from . import models, schemas
from .utils import SkipLimit



def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, sl: SkipLimit):
    return db.query(models.User).offset(sl.skip).limit(sl.limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = at.get_password_hash(user.password)
    db_user = models.User(email=user.email, username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user: schemas.User):
    db.query(models.User).filter(models.User.id == user.id).delete()
    db.commit()



def get_location(db: Session, location_id: int):
    return db.query(models.Location).filter(models.Location.id == location_id).first()

def get_location_by_postal_code(db: Session, postal_code: str):
    return db.query(models.Location).filter(models.Location.postal_code == postal_code).first()

def create_location(db: Session, location: schemas.LocationBase, country: schemas.Country):
    db_location = models.Location(
        postal_code = location.postal_code,
        name = location.name,
        description = location.description,
        country_id = country.id
    )
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location



def get_country(db: Session, country_id: int):
    return db.query(models.Country).filter(models.Country.id == country_id).first()

def get_country_by_name(db: Session, name: str):
    return db.query(models.Country).filter(models.Country.name == name).first()

def create_country(db: Session, country: schemas.CountryBase):
    db_country = models.Country(name=country.name)
    db.add(db_country)
    db.commit()
    db.refresh(db_country)
    return db_country



def get_type(db: Session, type_id: int):
    return db.query(models.ItemType).filter(models.ItemType.id == type_id).first()

def get_type_by_name(db: Session, type_name: str):
    return db.query(models.ItemType).filter(models.ItemType.type_name == type_name).first()

def create_type(db: Session, type: schemas.ItemTypeBase):
    db_item_type = models.ItemType(type_name=type.type_name)
    db.add(db_item_type)
    db.commit()
    db.refresh(db_item_type)
    return db_item_type



def get_unit(db: Session, unit_id: int):
    return db.query(models.Unit).filter(models.Unit.id == unit_id).first()

def get_unit_by_name(db: Session, unit_name: str):
    return db.query(models.Unit).filter(models.Unit.unit_name == unit_name).first()

def create_unit(db: Session, unit: schemas.UnitBase):
    db_unit = models.Unit(unit_name=unit.unit_name, unit_to_seconds=unit.unit_to_seconds)
    db.add(db_unit)
    db.commit()
    db.refresh(db_unit)
    return db_unit



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

def delete_item(db: Session, item: schemas.Item):
    db.query(models.Item).filter(models.Item.id == item.id).delete()
    db.commit()



def get_rent(db: Session, rent_id: int):
    return db.query(models.Rent).filter(models.Rent.id == rent_id).first()

def get_rent_by_item(db: Session, item: schemas.Item):
    return db.query(models.Rent).filter(models.Rent.item_id == item.id).first()

def get_owner_of_rent(db: Session, rent: schemas.Rent):
    return db.query(models.User).join(models.Item).join(models.Rent).filter(models.Rent.id == rent.id).first()

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

def create_rent(db: Session, rent: schemas.RentBase, item: schemas.Item, renter: schemas.User):
    unit: schemas.Unit = get_unit(db, item.unit_id)
    total_time_in_seconds = (rent.time_to - rent.time_to).total_seconds()
    price_total = item.price_per_unit / unit.unit_to_seconds * decimal.Decimal(total_time_in_seconds)

    db_rent = models.Rent(
        item_id = item.id,
        renter_id = renter.id,
        time_from = rent.time_from,
        time_to = rent.time_to,
        unit_id = item.unit_id,
        price_per_unit = item.price_per_unit,
        price_total = price_total
    )

    db.add(db_rent)
    db.commit()
    db.refresh(db_rent)
    return db_rent

def delete_rent(db: Session, rent: schemas.Rent):
    db_item = get_item(db, rent.item_id)
    db_item.available = True
    db.query(models.Rent).filter(models.Rent.id == rent.id).delete()
    db.commit()



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
    return db.query(models.RentRequest).join(models.Item).join(models.User)\
        .filter(models.Item.owner_id==models.User.id)\
        .filter(models.User.id==user.id)\
        .filter(models.RentRequest.time_to < datetime.now())\
        .offset(sl.skip).limit(sl.limit).all()

def get_rent_requests_mine(db: Session, user: schemas.User, sl: SkipLimit):
    return db.query(models.RentRequest).filter(models.RentRequest.renter_id == user.id)\
        .offset(sl.skip).limit(sl.limit).all()

def get_rent_requests_mine_not_expired(db: Session, user: schemas.User, sl: SkipLimit):
    return db.query(models.RentRequest)\
        .filter(models.RentRequest.renter_id == user.id)\
        .filter(models.RentRequest.time_to < datetime.now)\
        .offset(sl.skip).limit(sl.limit).all()

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
