from fastapi import Depends, Request
from jose import ExpiredSignatureError, JWTError, jwt
from config import settings
from app.models.user_model import User
from app.exceptions import (
    IncorrectTokenFormatException, 
    TokenExpired, 
    UserIsNotPresent
)
from app.services.sqlalchemy_repository import SqlAlchemyRepository
from app.core.database import get_session
from sqlalchemy.ext.asyncio import AsyncSession


def get_token(request: Request):
    token = request.cookies.get("access_token")
    return token

async def get_current_user(
        token: str = Depends(get_token), 
        session: AsyncSession = Depends(get_session)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET, settings.ALGORITHM
        )
        user_id: str = payload.get("sub")
        if not user_id:
            raise UserIsNotPresent
        
        user_repo = SqlAlchemyRepository(model=User, db_session=session)
        return await user_repo.get_single(id=user_id)
        
    except ExpiredSignatureError:
        raise TokenExpired
    
    except JWTError:
        raise IncorrectTokenFormatException
    
    except Exception as e:
        return None