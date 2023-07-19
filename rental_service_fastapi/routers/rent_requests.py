from fastapi import APIRouter, Depends, HTTPException, Body, status, Path
from typing import Annotated
from sqlalchemy.orm import Session
from pyxtension.streams import stream

from .. import schemas, crud
from ..database import get_db
from ..auth import auth_helper as at
from ..utils import SkipLimit, compare_hour_to_diff_time
from ..enum import RequestApprovedState

from datetime import datetime

router = APIRouter(
    prefix="/rent-requests",
    tags=["rent-requests"]
)


@router.get("/to-me/", response_model=list[schemas.RentRequest])
def read_requests_to_me(
    current_user: Annotated[schemas.User, Depends(at.get_current_active_user)],
    sl: SkipLimit,
    db: Session = Depends(get_db)
):
    return crud.get_rent_requests_to_me_not_expired(db, current_user, sl)


@router.get("/mine/", response_model=list[schemas.RentRequest])
def read_requests_mine(
    current_user: Annotated[schemas.User, Depends(at.get_current_active_user)],
    sl: SkipLimit,
    db: Session = Depends(get_db)
):
    return crud.get_rent_requests_mine_not_expired(db, current_user, sl)


@router.post("/send-request/", response_model=schemas.RentRequest)
def rent_selected_item(
    current_user: Annotated[schemas.User, Depends(at.get_current_active_user)],
    item_id: Annotated[int, Body()],
    rent_request_base: Annotated[schemas.RentRequestBase, Body()],
    db: Session = Depends(get_db)
):
    # Время не должно быть меньше(на какое то n минут) чем настоящее при создании реквеста
    # Todo: сделать это
    db_item = crud.get_item(db, item_id)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Item was not found"
        )
    if db_item.owner_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Self rent is not possible!"
        )
    if db_item.available == False:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Item is not yet available. Try later"
        )
    if not compare_hour_to_diff_time(rent_request_base.time_from, rent_request_base.time_to):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="You need to rent at least for one hour"
        )
    return crud.post_rent_request_for_item(db, current_user, db_item, rent_request_base)


@router.patch("/{rent_request_id}/", response_model=schemas.RentRequest)
def update_status(
    current_user: Annotated[schemas.User, Depends(at.get_current_active_user)],
    rent_request_id: Annotated[int, Path()],
    state: Annotated[RequestApprovedState, Body()],
    db: Session = Depends(get_db)
):
    db_request_list: schemas.RentRequest = stream(crud.get_rent_requests_to_me_not_expired(db, current_user, SkipLimit()))\
        .filter(lambda x: x.id == rent_request_id).to_list()
        
    if not db_request_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    
    db_request = db_request_list[0]
    
    if state == RequestApprovedState.yes:
        db_item: schemas.Item = crud.get_item(db, db_request.item_id)
        if not db_item:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if db_item.available == False:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Item is not yet available. Try later")
        db_renter: schemas.User = crud.get_user(db, db_request.renter_id)
        # должен ли менятся доступ к айтему сразу или позже?
  
        # пусть будет так: owner сам будет решать когда сделать айтем обратно доступным
        # при этом availability of item automaticaly становится false при создании rent
        crud.create_rent(db, db_request.time_from, db_request.time_to, db_item, db_renter)
        # удаление всех реквестов которые пересекаются во времени
        # возможно можно просто ставить no-state вместо удаления
    return crud.change_status_of_request(db, db_request, state)
    

@router.delete(
    "/{rent_request_id}/",
    status_code=204
)
def delete_rent_request(
    current_user: Annotated[schemas.User, Depends(at.get_current_active_user)],
    rent_request_id: Annotated[int, Path()],
    db: Session = Depends(get_db)
):
    db_rent_request = crud.get_rent_request(db, rent_request_id)
    if not crud.get_owner_of_item_requested(db, db_rent_request).id == current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    if db_rent_request:
        crud.delete_rent_request(db, db_rent_request)