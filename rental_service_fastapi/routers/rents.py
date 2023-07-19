from fastapi import APIRouter, Depends, HTTPException, Request, Form, Body, status, Path
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.security import OAuth2PasswordRequestForm

from .. import schemas, crud
from ..database import get_db
from ..auth import auth_helper as at
from ..utils import SkipLimit

router = APIRouter(
    prefix="/rents",
    tags=["rents"]
)

@router.get("/mine/", response_model=list[schemas.Rent])
def read_rented_by_me_items(
    current_user: Annotated[schemas.User, Depends(at.get_current_active_user)],
    sl: SkipLimit,
    db: Session = Depends(get_db),
    
):
    return crud.get_rents_by_owner(db, current_user, sl)


@router.get("/to-me/", response_model=list[schemas.Rent])
def read_rented_to_me_items(
    current_user: Annotated[schemas.User, Depends(at.get_current_active_user)],
    sl: SkipLimit,
    db: Session = Depends(get_db)
):
    return crud.get_rents_by_renter(db, current_user, sl)


@router.get(
    "/expired/",
    response_model=list[schemas.Rent]
)
def read_expired_rents(
    current_user: Annotated[schemas.User, Depends(at.get_current_active_user)],
    sl: SkipLimit,
    db: Session = Depends(get_db)
):
    return crud.get_expired_rents_by_owner(db, current_user, sl)


@router.get(
    "/{rent_id}/",
    response_model=schemas.Rent
)
def get_rent(
    rent_id: Annotated[int, Path()],
    current_user: Annotated[schemas.User, Depends(at.get_current_active_user)],
    db: Session = Depends(get_db)
):
    db_rent = crud.get_rent(db, rent_id)
    if not db_rent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if not (db_rent.renter_id == current_user.id or crud.get_owner_of_rent(db, db_rent).id == current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return db_rent


@router.delete(
    "/{rent_id}/",
    status_code=204,
)
def delete_rent(
    rent_id: Annotated[int, Path()],
    current_user: Annotated[schemas.User, Depends(at.get_current_active_user)],
    db: Session = Depends(get_db)
):
    db_rent = crud.get_rent(db, rent_id)
    if db_rent: 
        if crud.get_owner_of_rent(db, db_rent).id == current_user.id:
            crud.delete_rent(db, db_rent)
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
