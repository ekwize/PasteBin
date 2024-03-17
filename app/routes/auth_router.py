from fastapi import APIRouter, Depends, Response
from app.schemas.user_schemas import UserCreateModel, UserViewModel, UserLoginModel
from app.core.database import get_session
from app.services.sqlalchemy_repository import SqlAlchemyRepository
from app.models.user_model import User
from sqlalchemy.ext.asyncio import AsyncSession
from config import settings
from app.core.cache import get_redis_pool
from app.exceptions import UserAlreadyExists, UserIsNotAuth
from app.utils.auth import (
    TokenHelper, 
    auth_user, 
    create_tokens, 
)
from app.utils.dependencies import get_current_user, get_token
from aioredis import Redis
from logger import logger
import asyncpg


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/sign-up")
async def create_user(
    user_data: UserCreateModel, 
    session: AsyncSession = Depends(get_session)
) -> None:
    try:
        user_repo = SqlAlchemyRepository(model=User, db_session=session)
        current_user_email = await user_repo.get_single(email=user_data.email)
        current_user_username = await user_repo.get_single(username=user_data.username)


        if current_user_email or current_user_username:
            raise UserAlreadyExists

        await user_repo.create(user_data)
        
    except UserAlreadyExists as e:
        raise e
    except Exception as e:
        logger.error(e)
        

@router.post("/login", response_model=UserViewModel)
async def login_user(
    response: Response,
    user_data: UserLoginModel,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis_pool)
) -> UserViewModel:
    user_repo = SqlAlchemyRepository(model=User, db_session=session)
    user = await user_repo.get_single(email=user_data.email)
    user = await auth_user(response, redis, user_data, user)

    return UserViewModel(
        username=user.username, 
        email=user.email, 
        created_at=user.created_at
    )

@router.delete("/logout")
async def logout_user(
    response: Response, 
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis_pool)
) -> None:
    try:
        response.delete_cookie("access_token")
        await redis.delete(f"refresh_token:{current_user.id}")
    except:
        raise UserIsNotAuth


@router.post("/token/refresh")
async def refresh_tokens(
    response: Response, 
    access_token: str = Depends(get_token),
    redis: Redis = Depends(get_redis_pool)
) -> None:
    payload = TokenHelper.decode_expired_token(access_token)
    refresh_token = await redis.get(name=f"refresh_token:{payload['sub']}")
    if TokenHelper.check_token_expired(refresh_token):
        response.delete_cookie("access_token")
        await redis.delete(f"refresh_token:{payload['sub']}")
    else:
        try:
            tokens = create_tokens(
                {
                    "sub": payload["sub"],
                    "username": payload["username"]
                }, 
                expire_access_token=settings.ACCESS_TOKEN_EXPIRE,
                expire_refresh_token=settings.REFRESH_TOKEN_EXPIRE
            )
            response.set_cookie(key="access_token", value=tokens.access_token, httponly=True)
            await redis.set(
                name=f"refresh_token:{payload['sub']}", 
                value=tokens.refresh_token,
                ex=settings.REFRESH_TOKEN_EXPIRE
            )
        except Exception as e:
            logger.error(e)