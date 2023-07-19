from sqlalchemy.orm import Session
from ..auth import auth_helper as at
from datetime import datetime
import decimal
from typing import Annotated
from fastapi import Depends

from .. import models, schemas
from ..utils import SkipLimit

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