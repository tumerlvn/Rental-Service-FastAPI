from sqlalchemy.orm import Session
from ..auth import auth_helper as at
from datetime import datetime
import decimal
from typing import Annotated
from fastapi import Depends

from .. import models, schemas
from ..utils import SkipLimit


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