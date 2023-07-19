import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from ratelimit import RateLimitMiddleware, Rule
from ratelimit.backends.redis import RedisBackend
from ratelimit.backends.simple import MemoryBackend
from redis.asyncio import StrictRedis

from . import crud, models, schemas
from .database import engine, get_db
from .auth import auth_helper as at
from .routers import users, test, locations, types_and_units, items, rents, rent_requests, item_reviews



models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router)
# app.include_router(test.router)
app.include_router(locations.router)
app.include_router(types_and_units.router)
app.include_router(items.router)
app.include_router(rents.router)
app.include_router(rent_requests.router)
app.include_router(item_reviews.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["127.0.0.1", "localhost"]
)

app.add_middleware(
    RateLimitMiddleware,
    authenticate=at.get_current_user_id_and_group,
    backend=MemoryBackend(),
    config={
        r"^/users": [
            Rule(minute=30, block_time=60, group="user", zone="user-api"), 
            Rule(minute=1, block_time=10, group="guest", zone="user-api")
        ],
        r"^/items": [
            Rule(minute=30, block_time=60, group="user", zone="item-api"), 
            Rule(minute=1, block_time=10, group="guest", zone="item-api")
        ],
        r"^/rent-requests": [
            Rule(minute=30, block_time=60, group="user", zone="rent-request-api"), 
            Rule(minute=1, block_time=10, group="guest", zone="rent-request-api")
        ],
        r"^/location/": [
            Rule(minute=1, block_time=10, group="user", zone="location-api"), 
            Rule(minute=1, block_time=10, group="guest", zone="location-api")
        ],
        r"^/country/": [
            Rule(minute=1, block_time=10, group="user", zone="country-api"), 
            Rule(minute=1, block_time=10, group="guest", zone="country-api")
        ],
        r"^/rents": [
            Rule(minute=30, block_time=60, group="user", zone="rent-api"), 
            Rule(minute=1, block_time=10, group="guest", zone="rent-api")
        ],
        r"^/type/": [
            Rule(minute=1, block_time=10, group="user", zone="type-api"), 
            Rule(minute=1, block_time=10, group="guest", zone="type-api")
        ],
        r"^/unit/": [
            Rule(minute=1, block_time=10, group="user", zone="unit-api"), 
            Rule(minute=1, block_time=10, group="guest", zone="unit-api")
        ],
        r"^/item-reviews/": [
            Rule(minute=30, block_time=60, group="user", zone="item-review-api"), 
            Rule(minute=30, block_time=60, group="guest", zone="item-review-api")
        ],
    },
)


@app.get("/")
def welcome_page():
    return {"response": "hello"}

@app.post("/token", response_model=at.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    # db = next(get_db()) # wtf, somehow get_db() is not a call but a generator
    user = at.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = at.create_access_token(
        data={"sub": user.username}
    )
    return {"access_token": access_token, "token_type": "bearer"}


