from fastapi import APIRouter, Depends, HTTPException, Request, Form, Body
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.security import OAuth2PasswordRequestForm

from .. import schemas, crud
from ..database import get_db
from ..auth import auth_helper as at

router = APIRouter(
    tags=["types_and_units"]
)

@router.post(
    "/type/",
    response_model=schemas.ItemType,
    dependencies=[Depends(at.allow_create_resource)]
)
def create_type(type: schemas.ItemTypeBase, db: Session = Depends(get_db)):
    db_type = crud.get_type_by_name(db, type.type_name)
    if db_type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Type already exists")
    return crud.create_type(db, type)

@router.post(
    "/unit/",
    response_model=schemas.Unit,
    dependencies=[Depends(at.allow_create_resource)]
)
def create_unit(unit: schemas.UnitBase, db: Session = Depends(get_db)):
    db_unit = crud.get_unit_by_name(db, unit.unit_name)
    if db_unit:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unit already exists")
    return crud.create_unit(db, unit)