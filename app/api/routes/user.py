from typing import Annotated
from fastapi import APIRouter, Depends
from app.api.actions.auth import authenticate_client
from app.schemas.user_scheme import UserCreateModel, UserLoginModel
from app.schemas.oauth_scheme import AccessToken
from app.models.user_model import User
from app.exceptions import UserAlreadyExists, TokenWasNotFound
from app.utils.security import create_tokens
from app.utils.token_helper import TokenHelper
from app.services.user_service import UserService
from app.api.dependencies import user_service, redis_service
from app.services.redis_service import RedisService
from config import settings
from app.api.actions.auth import get_current_user, oauth2_scheme

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/signup")
async def create_user(
    user_data: UserCreateModel, 
    user_service: UserService = Depends(user_service)
) -> None:
    try:
        await user_service.create(user_data)
    except:
        raise UserAlreadyExists
        
        
@router.post("/login", response_model=AccessToken)
async def login_user(
    user_data: UserLoginModel,
    redis_service: Annotated[RedisService, Depends(redis_service)],
) -> AccessToken:
    user = await authenticate_client(username=user_data.username, password=user_data.password)

    tokens = create_tokens(user_id=user.id, username=user.username)

    await redis_service.set(
            name=f"refresh_token:{user.id}", 
            value=tokens.refresh_token,
            ex=settings.REFRESH_TOKEN_EXPIRE
        )
    return AccessToken(access_token=tokens.access_token)                        
        

@router.delete("/logout")
async def logout_user(
    current_user: Annotated[User, Depends(get_current_user)],
    redis_service: Annotated[RedisService, Depends(redis_service)]
) -> None:
    if not current_user:
        return
    await redis_service.delete(f"refresh_token:{current_user.id}")
    

@router.post("/token/refresh", response_model=AccessToken)
async def refresh_tokens(
    access_token: Annotated[str, Depends(oauth2_scheme)],
    redis_service: Annotated[RedisService, Depends(redis_service)]
) -> AccessToken:
    if not access_token:
        raise TokenWasNotFound
    
    payload = TokenHelper.decode_expired_token(access_token)
    refresh_token = await redis_service.get(name=f"refresh_token:{payload['sub']}")

    if refresh_token:
        tokens = create_tokens(payload["sub"], payload["username"])
        await redis_service.set(
            name=f"refresh_token:{payload['sub']}", 
            value=tokens.refresh_token,
            ex=settings.REFRESH_TOKEN_EXPIRE
        )
        return AccessToken(access_token=tokens.access_token)   
            


    