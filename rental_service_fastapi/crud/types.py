from sqlalchemy.orm import Session
from ..auth import auth_helper as at
from datetime import datetime
import decimal
from typing import Annotated
from fastapi import Depends

from .. import models, schemas
from ..utils import SkipLimit

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