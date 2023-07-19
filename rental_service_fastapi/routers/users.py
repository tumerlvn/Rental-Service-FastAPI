from fastapi import APIRouter, Depends, HTTPException, Request, Form, Body
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.security import OAuth2PasswordRequestForm

from .. import schemas, crud
from ..database import get_db
from ..auth import auth_helper as at
from .forms import UserCreateForm
from ..utils import SkipLimit

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/me/", response_model=schemas.User)
async def read_users_me(
    current_user: Annotated[schemas.User, Depends(at.get_current_active_user)]
):
    return current_user

@router.get(
    "/", 
    response_model=list[schemas.User], 
    dependencies=[Depends(at.allow_create_resource)]
)
def read_users(sl: SkipLimit, db: Session = Depends(get_db)):
    users = crud.get_users(db, sl)
    return users

@router.post(
    "/",
    response_model=schemas.User,
    dependencies=[Depends(at.allow_create_resource)]
)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
        Попытается создать юзера, если не авторизован - ошибка,
        если не админ - тоже
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    return crud.create_user(db=db, user=user)

@router.post("/register/", response_model=schemas.User)
async def register_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    email: Annotated[str, Form()],
    db: Session = Depends(get_db)
):
    form = UserCreateForm(username=form_data.username, email=email, password=form_data.password)
    if form.is_valid():
        user = schemas.UserCreate(
            username=form.username,
            email=form.email,
            password=form.password
        )
        try:
            crud.create_user(db, user)
        except IntegrityError:
            raise HTTPException(status_code=400, detail="Duplicate username or email")
        return crud.get_user_by_email(db, user.email)
    else:
        raise HTTPException(status_code=400, detail=form.errors)

@router.delete(
    "/",
    status_code=204,
    dependencies=[Depends(at.allow_create_resource)]
)
def delete_user(username: Annotated[str, Body()], db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, username)
    if user:
        crud.delete_user(db, user)
