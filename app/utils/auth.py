from fastapi import Response
from passlib.context import CryptContext
from config import settings
from .token_helper import TokenHelper
from typing import NamedTuple
from app.services.redis_service import RedisService


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Tokens(NamedTuple):
    access_token: str
    refresh_token: str


def create_tokens(data: dict) -> Tokens:
    try:  
        access_token = TokenHelper.encode(
            payload=data, 
            expire_period=settings.ACCESS_TOKEN_EXPIRE
        )
        refresh_token = TokenHelper.encode(
            payload=data,
            expire_period=settings.REFRESH_TOKEN_EXPIRE
        )
        return Tokens(access_token, refresh_token)
    
    except Exception as e:
        raise e
    
async def set_tokens(
        response: Response, 
        user_id: str,
        username: str,
        redis_service: RedisService
) -> None:
    try:
        tokens = create_tokens(
            {
                "sub": str(user_id), 
                "username": str(username)
            },
        )
    
        response.set_cookie("access_token", str(tokens.access_token), httponly=True)
        
        await redis_service.set(
            name=f"refresh_token:{user_id}", 
            value=tokens.refresh_token,
            ex=settings.REFRESH_TOKEN_EXPIRE
        )
    except Exception as e:
        raise e


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)
    


