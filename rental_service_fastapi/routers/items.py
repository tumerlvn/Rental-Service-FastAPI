from fastapi import APIRouter, Depends, HTTPException, Request, Form, Body, Path, status, Query
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.security import OAuth2PasswordRequestForm

from .. import schemas, crud
from ..database import get_db
from ..auth import auth_helper as at
from ..utils import SkipLimit

router = APIRouter(
    prefix="/items",
    tags=["items"]
)

@router.get("/mine/", response_model=list[schemas.Item])
async def read_my_items(
    current_user: Annotated[schemas.User, Depends(at.get_current_active_user)],
    sl: SkipLimit,
    db: Session = Depends(get_db),
):
    return crud.get_items_by_user(db, current_user, sl)

@router.post("/create/", response_model=schemas.Item)
async def create_item(
    current_user: Annotated[schemas.User, Depends(at.get_current_active_user)],
    item: schemas.ItemBase,
    unit_name: Annotated[str, Body()],
    type_name: Annotated[str, Body()],
    location_postal_code: Annotated[str, Body()],
    db: Session = Depends(get_db),
):
    db_unit = crud.get_unit_by_name(db, unit_name)
    if not db_unit:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such unit")
    db_type = crud.get_type_by_name(db, type_name)
    if not db_type:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such type")
    db_location = crud.get_location_by_postal_code(db, location_postal_code)
    if not db_location:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No such location")
    return crud.create_item(db, item, db_unit, db_type, current_user, db_location)

@router.patch("/availability/{item_id}/")
def change_availability_of_item(
    item_id: Annotated[int, Path()],
    current_user: Annotated[schemas.User, Depends(at.get_current_active_user)],
    is_available: Annotated[bool, Query()],
    db: Session = Depends(get_db)
):
    db_item = crud.get_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if db_item.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return crud.update_availability_of_item(db, db_item, is_available)

@router.get("/{item_id}/", response_model=schemas.Item)
async def read_item(
    item_id: Annotated[int, Path()],
    current_user: Annotated[schemas.User, Depends(at.get_current_active_user)],
    db: Session = Depends(get_db)
):
    db_item = crud.get_item(db, item_id)
    if not db_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return db_item

@router.get("/", response_model=list[schemas.Item])
async def read_items(
    current_user: Annotated[schemas.User, Depends(at.get_current_active_user)],
    sl: SkipLimit,
    db: Session = Depends(get_db),
    is_available: Annotated[bool, Query()] = True
):
    if is_available is None:
        return crud.get_items(db, sl)
    return crud.get_available_items(db, is_available, sl)
