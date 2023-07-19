from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel
from .. import crud, schemas
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, status
from typing import Annotated, List, Tuple
from ..database import get_db
from enum import Enum
from ratelimit.types import Scope
from ratelimit.auths import EmptyInformation
from ratelimit.auths.jwt import create_jwt_auth

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

jwt_auth = create_jwt_auth(SECRET_KEY, ALGORITHM)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str):
    user = crud.get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[schemas.User, Depends(get_current_user)]
):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

class Role(str, Enum):
    admin = "admin"
    user = "user"
    guest = "guest"

class RoleChecker:
    def __init__(self, allowed_roles: List[Role]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: schemas.User = Depends(get_current_active_user)):
        if user.role not in self.allowed_roles:
            # logger.debug(f"User with role {user.role} not in {self.allowed_roles}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted")


allow_create_resource = RoleChecker([Role.admin])

async def get_current_user_id_and_group(
    scope: Scope
) -> Tuple[str, str]:
    client = scope['client']
    # print(client)
    headers = dict(scope['headers'])
    token_bytes = headers.get(b'authorization')
    if token_bytes:
        bearer, _ , token = token_bytes.decode("utf-8").partition(" ")
        current_user = await get_current_user(token, next(get_db()))
        current_active_user = await get_current_active_user(current_user)
        return current_active_user.username, current_active_user.role
    print(Role.guest.value)
    return str(client), Role.guest.value