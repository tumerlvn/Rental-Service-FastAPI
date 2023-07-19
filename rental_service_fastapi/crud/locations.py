from sqlalchemy.orm import Session
from ..auth import auth_helper as at
from datetime import datetime
import decimal
from typing import Annotated
from fastapi import Depends

from .. import models, schemas
from ..utils import SkipLimit

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