from typing import Annotated
from fastapi import APIRouter, Depends, Response
from app.schemas.user_schemas import UserCreateModel, UserViewModel, UserLoginModel
from app.models.user_model import User
from app.exceptions import UserAlreadyExists, UserIsNotAuth, UserWasNotFound, IncorrectUsernameOrPassword
from app.utils.auth import verify_password, set_tokens
from app.utils.token_helper import TokenHelper
from app.utils.dependencies import get_current_user, get_token
from app.services.user_service import UserService
from .dependencies import user_service, redis_service
from app.services.redis_service import RedisService


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/signup")
async def create_user(
    user_data: UserCreateModel, 
    user_service: UserService = Depends(user_service)
) -> None:
    user_email = await user_service.get_single(email=user_data.email)
    user_username = await user_service.get_single(username=user_data.username)

    if user_email:
        raise UserAlreadyExists(reason="email")
    elif user_username:
        raise UserAlreadyExists(reason="username")
    
    await user_service.create(user_data)
        
        

@router.post("/login", response_model=UserViewModel)
async def login_user(
    response: Response,
    user_data: UserLoginModel,
    user_service: Annotated[UserService, Depends(user_service)],
    redis_service: Annotated[RedisService, Depends(redis_service)],
) -> UserViewModel:
    user = await user_service.get_single(username=user_data.username)

    if not user:
        raise UserWasNotFound
    
    if not verify_password(user_data.password, str(user.password)):
        raise IncorrectUsernameOrPassword
    
    await set_tokens(response, user.id, user.username, redis_service)

    return user
        


@router.delete("/logout")
async def logout_user(
    response: Response, 
    current_user: Annotated[User, Depends(get_current_user)],
    redis_service: Annotated[RedisService, Depends(redis_service)]
) -> None:
    try:
        response.delete_cookie("access_token")
        await redis_service.delete(f"refresh_token:{current_user.id}")
    except:
        raise UserIsNotAuth


@router.post("/token/refresh")
async def refresh_tokens(
    response: Response, 
    access_token: Annotated[str, Depends(get_token)],
    redis_service: Annotated[RedisService, Depends(redis_service)]
) -> None:
    if not TokenHelper.check_token_expired(access_token):
        return 
    payload = TokenHelper.decode_expired_token(access_token)
    refresh_token = await redis_service.get(name=f"refresh_token:{payload['sub']}")
    if TokenHelper.check_token_expired(refresh_token):
        response.delete_cookie("access_token")
        await redis_service.delete(f"refresh_token:{payload['sub']}")
    else:
        await set_tokens(response, payload['sub'], payload['username'], redis_service)
            


    