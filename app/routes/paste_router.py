from typing import List
from fastapi import APIRouter, Depends
from app.schemas.paste_schemas import (
    PasteCreateModel, 
    PasteForSaveModel,
    PasteViewModel,
    PasteUpdateModel,
    PasteAuthModel,
)
from app.exceptions import (
    PasteWasNotFound, 
    PasteWasNotCreated, 
    PasteOwnExc,
    PasteWasNotRemoved,
    PasteWasNotUpdated,
    UserWasNotFound
)
from app.utils.paste import (
    create_paste_id, 
    verify_paste_password
)
from app.models.user_model import User, PortalRole
from app.utils.dependencies import get_current_user
from datetime import datetime, timezone
from app.core.storage import s3, bucket
from app.services.sqlalchemy_repository import SqlAlchemyRepository
from app.core.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.paste_model import Paste
from app.exceptions import UserIsNotAuth
from app.utils.paste import create_paste_id
from app.exceptions import IncorrectPastePassword
from app.core.cache import get_redis_pool
from aioredis import Redis
from fastapi_cache.decorator import cache
from worker.tasks import del_exp_paste
from logger import logger


router = APIRouter(
    prefix="",
    tags=["Paste"]
)

@router.post("/")
async def create_paste(
    paste_data: PasteCreateModel, 
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis_pool)
):
    try:
        expires_at = datetime.utcnow() + paste_data.expiration if paste_data.expiration else None
        paste_id = await redis.rpop("hashes")
        
        if not paste_id:
            paste_id = create_paste_id()
            logger.info(
                msg=f"No hash in the 'hashes'"
            )

        if current_user:
            paste = PasteForSaveModel(
                id=paste_id,
                title=paste_data.title,
                category=paste_data.category,
                password=paste_data.password,
                exposure=paste_data.exposure,
                expiration=paste_data.expiration,
                user_id=current_user.id,
                username=current_user.username,
                role=PortalRole.ROLE_PORTAL_USER,
                expires_at=expires_at
            )
        else:
            paste = PasteForSaveModel(
                id=paste_id,
                title=paste_data.title,
                category=paste_data.category,
                password=paste_data.password,
                exposure="Public",
                expiration=paste_data.expiration,
                role=PortalRole.ROLE_PORTAL_GUEST,
                expires_at=expires_at
            )
        
        paste_repo = SqlAlchemyRepository(Paste, session)

        await paste_repo.create(paste)
        s3.put_object(Bucket=bucket(), Key=f"{paste_id}", Body=paste_data.text)
    except Exception as e:
        logger.error(
            msg=e,
            extra={
                "user_id": current_user.id if current_user else None,
            }
        )
        raise PasteWasNotCreated


@router.post("/{paste_auth_data.paste_id}", response_model=PasteViewModel)
async def view_paste(
    paste_auth_data: PasteAuthModel,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> PasteViewModel:
    paste_repo = SqlAlchemyRepository(Paste, session)
    paste = await paste_repo.get_single(id=paste_auth_data.id)

    if not paste:
        raise PasteWasNotFound
    
    await del_exp_paste(session)

    response = s3.get_object(Bucket=bucket(), Key=f'{paste_auth_data.id}')
    paste_text = response["Body"].read().decode('utf-8')

    if current_user and paste.user_id == current_user.id:
        return PasteViewModel(
                id=paste.id,
                text=paste_text,
                username=paste.username,
                title=paste.title,
                category=paste.category,
                exposure=paste.exposure,
                expiration=paste.expiration,
                expires_at=paste.expires_at,
                created_at=paste.created_at
            )
        
    if not verify_paste_password(paste, paste_auth_data.password):
        raise IncorrectPastePassword
    
    if paste.expiration == 0:
        paste_repo.delete(id=paste_auth_data.id)
        s3.delete_object(Bucket=bucket(), Key=f'{paste_auth_data.id}')
    
    return PasteViewModel(
            id=paste.id,
            text=paste_text,
            username=paste.username,
            title=paste.title,
            category=paste.category,
            exposure=paste.exposure,
            expiration=paste.expiration,
            expires_at=paste.expires_at,
            created_at=paste.created_at
        )
    
    
    
@router.delete("/delete/{paste_id}")
async def delete_paste(
    paste_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> None:
    try:
        if not current_user:
            raise UserIsNotAuth
        
        paste_repo = SqlAlchemyRepository(Paste, session)
        paste = await paste_repo.get_single(id=paste_id)

        if not paste:
            raise PasteWasNotFound

        if current_user.id != paste.user_id:
            raise PasteOwnExc
        
        
        await paste_repo.delete(id=paste_id)
        s3.delete_object(Bucket=bucket(), Key=f'{paste.id}')

    except (UserIsNotAuth, PasteWasNotFound, PasteOwnExc) as e:
        raise e
    except Exception as e:
        logger.error(
            msg=e,
            extra={
                "user_id": current_user.id,
                "paste_id": paste.id,
            }
        )
        raise PasteWasNotRemoved


@router.put("/edit_paste/{paste_id}")
async def edit_paste(
    paste_id: str,
    new_paste_data: PasteCreateModel,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> None:
    if not current_user:
        raise UserIsNotAuth
    
    paste_repo = SqlAlchemyRepository(Paste, session)
    paste = await paste_repo.get_single(id=paste_id)

    if not paste:
        raise PasteWasNotFound

    if current_user.id != paste.user_id:
        raise PasteOwnExc

    expires_at = datetime.utcnow() + new_paste_data.expiration if new_paste_data.expiration else None

    new_paste = PasteUpdateModel(
        title=new_paste_data.title,
        category=new_paste_data.category,
        password=new_paste_data.password,
        exposure=new_paste_data.exposure,
        expiration=new_paste_data.expiration,
        expires_at=expires_at,
        updated_at=datetime.utcnow()
    )

    try:
        await paste_repo.update(new_paste, id=paste.id)
        s3.put_object(Bucket=bucket(), Key=f"{paste.id}", Body=new_paste_data.text)
    except Exception as e:
        logger.error(
            msg=e,
            extra={
                "user_id": current_user.id,
                "paste_id": paste.id,
            }
        )
        raise PasteWasNotUpdated



@router.get("/pub/{username}")
@cache(expire=30)
async def get_user_pastes(
    username: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    user_repo = SqlAlchemyRepository(User, session)
    paste_repo = SqlAlchemyRepository(Paste, session)
    user = await user_repo.get_single(username=username)

    if not user:
        raise UserWasNotFound

    try:
        if current_user and current_user.id == user.id:
            all_pastes = await paste_repo.get_all(user_id=user.id)
            pastes_info = []
            for paste in all_pastes:
                paste = PasteViewModel(
                    id=paste.id,
                    text=None,
                    username=paste.username,
                    title=paste.title,
                    category=paste.category,
                    exposure=paste.exposure,
                    expiration=paste.expiration,
                    expires_at=paste.expires_at,
                    created_at=paste.created_at
                )
                pastes_info.append(paste) 
            return pastes_info
        only_pub_pastes = await paste_repo.get_all(user_id=user.id, exposure="Public")
        return only_pub_pastes
    except Exception as e:
        logger.error(
            msg=e,
            extra={
                "user_id": current_user.id,
                "username": username
            }
        )
        raise PasteWasNotFound

    
    

