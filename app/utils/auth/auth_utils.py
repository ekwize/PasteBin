from fastapi import Response, Depends
from app.models.user_model import User
from app.schemas.user_schemas import UserCreateModel
from passlib.context import CryptContext
from app.exceptions import UserWasNotFound, IncorrectEmailOrPassword
from datetime import datetime, timedelta
from config import settings
import base64
import secrets
from .token_helper import TokenHelper
from app.core.cache import get_redis_pool
from typing import NamedTuple
from aioredis import Redis


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Tokens(NamedTuple):
    access_token: str
    refresh_token: str


def create_tokens(data: dict, 
                  expire_access_token: int,
                  expire_refresh_token: int
) -> Tokens:
    try:  
        
        access_token = TokenHelper.encode(
            payload=data, 
            expire_period=expire_access_token
        )

        refresh_token = TokenHelper.encode(
            payload=data,
            expire_period=expire_refresh_token
        )
        
        return Tokens(access_token, refresh_token)
    
    except Exception as e:
        raise e

async def auth_user(
        response: Response,
        redis: Redis,
        user_data: UserCreateModel, 
        user: User,
) -> User:
    try:
        if not user:
            raise UserWasNotFound
        
        if not verify_password(user_data.password, str(user.password)):
            raise IncorrectEmailOrPassword
        
        tokens = create_tokens(
            {
                "sub": str(user.id), 
                "username": str(user.username)
            },
            expire_access_token=settings.ACCESS_TOKEN_EXPIRE,
            expire_refresh_token=settings.REFRESH_TOKEN_EXPIRE
        )
    
        response.set_cookie("access_token", str(tokens.access_token), httponly=True)
        await redis.set(
            name=f"refresh_token:{user.id}", 
            value=tokens.refresh_token,
            ex=settings.REFRESH_TOKEN_EXPIRE
        )
        return user
        
    
    except Exception as e:
        raise e


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)
    


