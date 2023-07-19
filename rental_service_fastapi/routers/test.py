from fastapi import APIRouter, Form, Depends, Query
from sqlalchemy.orm import Session
from typing import Annotated

from ..models import User, Location, Country, Item, ItemType, Unit
from ..database import get_db
from .. import crud

router = APIRouter(
    prefix="/test",
    tags=["test"]
)

@router.post("/")
def post_test(
    email: Annotated[str, Form(regex= '^[a-z0-9]+[\._]?[ a-z0-9]+[@]\w+[. ]\w{2,3}$')],
):
    return {"uspeh": True}

@router.post("/insert_items/")
def insert_items(db: Session = Depends(get_db)):
    newCountry = Country(name="Kazakhstan")
    db.add(newCountry)
    db.commit()
    db.refresh(newCountry)
    newLocation = Location(
        postal_code = "010000",
        name = "Astana",
        description = "Capital of Kazakhstan",
    )
    newLocation.country = newCountry
    db.add(newLocation)
    db.commit()
    db.refresh(newLocation)
    newUser = User(
        username = "tamer",
        email = "tamer07@mail.ru",
        hashed_password = "hashedString",
        registration_time = "2023-04-10T10:39:37"
    )
    newUser.location = newLocation
    newUser.location_details = newUser.location.description
    db.add(newUser)
    db.commit()
    db.refresh(newUser)
    newType = ItemType(
        type_name = "apartment"
    )
    db.add(newType)
    db.commit()
    db.refresh(newType)
    newUnit = Unit(
        unit_name = "day"
    )
    db.add(newUnit)
    db.commit()
    db.refresh(newUnit)
    newItem = Item(
        item_name = "Apartment in Astana",
        description = "Very good apartment",
        available = True
    )
    newItem.location = newLocation
    newItem.owner = newUser
    newItem.unit = newUnit
    newItem.item_type = newType
    newItem.price_per_unit = 20
    newItem.item_location = newItem.location.name
    db.add(newItem)
    db.commit()
    db.refresh(newItem)


@router.get("/get_owner_of_rent/{rent_id}/")
def get_owner_of_rent(rent_id = Annotated[int, Query()], db: Session = Depends(get_db)):

    db_rent = crud.get_rent(db, rent_id)
    return crud.get_owner_of_rent(db, db_rent)