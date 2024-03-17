from datetime import datetime, timedelta, timezone

from jose import ExpiredSignatureError, JWTError, jwt

from config import settings
from app.exceptions.auth_exc import (
    IncorrectTokenFormatException, 
    TokenExpired, 
)
from typing import Any


class TokenHelper:
    @staticmethod
    def encode(payload: dict, expire_period: int = 3600) -> str:
        token = jwt.encode(
            {
                **payload,
                "exp": datetime.utcnow() + timedelta(seconds=expire_period),
            },
            key=settings.SECRET,
            algorithm=settings.ALGORITHM,
        )
        return token

    @staticmethod
    def decode(token: str) -> dict[str, Any]:
        try:
            return jwt.decode(
                token,
                settings.SECRET,
                settings.ALGORITHM,
            )
        except ExpiredSignatureError:
            raise TokenExpired
    
        except JWTError:
            raise IncorrectTokenFormatException

    @staticmethod
    def decode_expired_token(token: str) -> dict[str, Any]:
        try:
            return jwt.decode(
                token,
                settings.SECRET,
                settings.ALGORITHM,
                options={"verify_exp": False},
            )
        except ExpiredSignatureError:
            raise TokenExpired
    
        except JWTError:
            raise IncorrectTokenFormatException
        
    @staticmethod
    def check_token_expired(token: str) -> bool:
        try:
            payload = jwt.decode(
                token, 
                settings.SECRET, 
                settings.ALGORITHM
            )
        except ExpiredSignatureError:
            return True
        
        except Exception:
            return False