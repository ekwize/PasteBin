from config import settings
from .token_helper import TokenHelper
from app.schemas.oauth_scheme import Tokens


def create_tokens(user_id: str, username: str) -> Tokens:
    try:  
        payload = {
            "sub": str(user_id), 
            "username": str(username)
        }
        access_token = TokenHelper.encode(
            payload=payload, 
            expire_period=settings.ACCESS_TOKEN_EXPIRE
        )
        refresh_token = TokenHelper.encode(
            payload=payload,
            expire_period=settings.REFRESH_TOKEN_EXPIRE
        )
        return Tokens(access_token=access_token, refresh_token=refresh_token)
    
    except Exception as e:
        raise e
