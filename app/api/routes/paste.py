from typing import Annotated
from fastapi import APIRouter, Depends
from app.schemas.paste_scheme import (
    PasteCreateModel, 
    PasteForUserModel,
    PasteViewModel,
    PasteUpdateModel,
    PasteAuthModel,
)
from app.exceptions import (
    PasteWasNotFound, 
    PasteOwnExc,
    UserWasNotFound
)
from app.services.user_service import UserService
from app.utils.paste import verify_paste_password, create_paste_id
from app.models.user_model import User, PortalRole
from app.api.actions.auth import get_current_user
from datetime import datetime, timedelta
from app.exceptions import UserIsNotAuth
from app.exceptions import IncorrectPastePassword
from fastapi_cache.decorator import cache
from logger import logger
from app.api.dependencies import redis_service, paste_service, user_service
from app.services.redis_service import RedisService
from app.services.paste_service import PasteService


router = APIRouter(
    prefix="/paste",
    tags=["Paste"]
)

@router.post("/create", response_model=PasteViewModel)
async def create_paste(
    paste_data: PasteForUserModel, 
    current_user: Annotated[User, Depends(get_current_user)],
    redis_service: Annotated[RedisService, Depends(redis_service)],
    paste_service: Annotated[PasteService, Depends(paste_service)]
) -> PasteViewModel:
    
    expires_at = datetime.utcnow() + paste_data.expiration if paste_data.expiration is not None else None
    paste_id = await redis_service.get_hash()

    if not paste_id:
        paste_id = create_paste_id()
        logger.info(
            msg="No hash in the 'hashes'"
        )

    if current_user:
        paste = PasteCreateModel(
            id=paste_id,
            user_id=current_user.id,
            role=PortalRole.ROLE_PORTAL_USER,
            username=current_user.username,
            **paste_data.model_dump(),
            expires_at=expires_at
        )
    else:
        paste = PasteCreateModel(
            id=paste_id,
            role=PortalRole.ROLE_PORTAL_GUEST,
            title=paste_data.title,
            category=paste_data.category,
            password=paste_data.password,
            exposure="Public",
            expiration=paste_data.expiration,
            expires_at=expires_at
        )

    return await paste_service.create(paste, paste_data.text, paste_id)
    


@router.post("/{id}", response_model=PasteViewModel)
async def view_paste(
    paste_auth_data: PasteAuthModel,
    paste_service: Annotated[PasteService, Depends(paste_service)],
    current_user: User = Depends(get_current_user),
) -> PasteViewModel:
    
    paste = await paste_service.get_single(paste_auth_data.id)
    view_paste = PasteViewModel(**paste.model_dump())

    if current_user and paste.user_id == current_user.id:
        return view_paste
    
    if paste.exposure == "Private":
        raise PasteOwnExc
        
    if not verify_paste_password(paste, paste_auth_data.password):
        raise IncorrectPastePassword

    if paste.expiration == timedelta(seconds=0):
        await paste_service.delete(paste_auth_data.id)

    return view_paste
    
        
    
@router.delete("/delete/{paste_id}")
async def delete_paste(
    paste_id: str,
    paste_service: Annotated[PasteService, Depends(paste_service)],
    current_user: User = Depends(get_current_user),
) -> None:
    if not current_user:
        raise UserIsNotAuth
    
    paste = await paste_service.get_single(paste_id)
    if not paste:
        raise PasteWasNotFound

    if current_user.id != paste.user_id:
        raise PasteOwnExc
    
    await paste_service.delete(paste_id)



@router.put("/edit_paste/{paste_id}")
async def edit_paste(
    paste_id: str,
    new_paste_data: PasteForUserModel,
    paste_service: Annotated[PasteService, Depends(paste_service)],
    current_user: User = Depends(get_current_user),
) -> None:

    if not current_user:
        raise UserIsNotAuth
    
    paste = await paste_service.get_single(paste_id)

    if not paste:
        raise PasteWasNotFound

    if current_user.id != paste.user_id:
        raise PasteOwnExc

    expires_at = datetime.utcnow() + new_paste_data.expiration if new_paste_data.expiration else None

    new_paste = PasteUpdateModel(
        **new_paste_data.__dict__,
        expires_at=expires_at,
    )


    await paste_service.update(paste_id, new_paste, new_paste_data.text)
    



@router.get("/pub/{username}")
@cache(expire=30)
async def get_user_pastes(
    username: str,
    paste_service: Annotated[PasteService, Depends(paste_service)],
    user_service: Annotated[UserService, Depends(user_service)],
    current_user: User = Depends(get_current_user),
) -> list[PasteViewModel]:
    user = await user_service.get_single(username=username)

    if not user:
        raise UserWasNotFound

    try:
        if current_user and current_user.id == user.id:
            all_pastes = await paste_service.get_all(user_id=user.id)
            return all_pastes
        only_pub_pastes = await paste_service.get_all(user_id=user.id, exposure="Public")
        return only_pub_pastes
    except Exception as e:
        logger.error(
            msg=e,
            extra={
                "user_id": current_user.id,
                "username": username
            }
        )


    
    

