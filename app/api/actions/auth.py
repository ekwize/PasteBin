from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from config import settings
from app.models.user_model import User
from app.exceptions import (
    IncorrectTokenFormatException, 
    TokenExpired, 
    UserIsNotPresent,
    IncorrectUsernameOrPassword
)
from app.services.user_service import UserService
from app.api.dependencies import user_service
from typing import Annotated
from app.utils.auth import verify_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
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
    

async def authenticate_client(username: str, password: str):
    client = await user_service().get_single(username=username)

    if not (client and verify_password(password, client.password)):
        raise IncorrectUsernameOrPassword

    return client
