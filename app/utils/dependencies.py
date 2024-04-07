from fastapi import Depends, Request
from jose import ExpiredSignatureError, JWTError, jwt
from config import settings
from app.models.user_model import User
from app.exceptions import (
    IncorrectTokenFormatException, 
    TokenExpired, 
    UserIsNotPresent
)
from app.services.user_service import UserService
from app.api.dependencies import user_service
from typing import Annotated


def get_token(request: Request):
    token = request.cookies.get("access_token")
    return token

async def get_current_user(
        token: Annotated[str, Depends(get_token)],
        user_service: Annotated[UserService, Depends(user_service)]
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET, settings.ALGORITHM
        )
        user_id: str = payload.get("sub")
        
        if not user_id:
            raise UserIsNotPresent

        return await user_service.get_single(id=user_id)
        
    except ExpiredSignatureError:
        raise TokenExpired
    
    except JWTError:
        raise IncorrectTokenFormatException
    
    except Exception as e:
        return None