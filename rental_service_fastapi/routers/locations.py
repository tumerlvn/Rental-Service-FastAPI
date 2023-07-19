from fastapi import APIRouter, Depends, HTTPException, Request, Form, Body
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.security import OAuth2PasswordRequestForm

from .. import schemas, crud
from ..database import get_db
from ..auth import auth_helper as at

router = APIRouter(
    tags=["locations"]
)

@router.post(
    "/location/",
    response_model=schemas.Location,
    dependencies=[Depends(at.allow_create_resource)]
)
def create_location(location: schemas.LocationBase, country: schemas.CountryBase, db: Session = Depends(get_db)):
    db_country = crud.get_country_by_name(db, country.name)
    if not db_country:
        raise HTTPException(status_code=400, detail="Country doesn't exists")
    db_location = crud.get_location_by_postal_code(db, location.postal_code)
    if db_location:
        raise HTTPException(status_code=400, detail="Location already exists")
    return crud.create_location(db, location, db_country)

@router.post(
    "/country/",
    response_model=schemas.Country,
    dependencies=[Depends(at.allow_create_resource)]
)
def create_country(country: schemas.CountryBase, db: Session = Depends(get_db)):
    db_country = crud.get_country_by_name(db, name=country.name)
    if db_country:
        raise HTTPException(status_code=400, detail="Country already exists")
    return crud.create_country(db=db, country=country)