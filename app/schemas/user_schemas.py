import base64
import secrets
from app.schemas.base_schema import Base
from pydantic import EmailStr, field_validator
from datetime import datetime
from typing import Optional
import re
from app.exceptions import IncorrectPassword


def create_username():
    id = secrets.token_bytes(6)
    hash = base64.urlsafe_b64encode(id)
    unique_id = hash.decode()
    return 'User_' + unique_id


class UserCreateModel(Base):
    """Model to create user"""

    username: Optional[str]
    email: EmailStr
    password: str

    @field_validator('password')
    def validate_password(cls, v: str) -> str:
        password_regex = r'^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])[!@#$%^&*(),.?":{}|<>\w-]{8,25}$'

        if not re.fullmatch(password_regex, v):
            raise IncorrectPassword
        return v
    
    @field_validator('username')
    def validate_username(cls, v: str) -> str:
        if not v:
            v = create_username()
        return v

class UserLoginModel(Base):
    """Model for user authorization"""

    email: EmailStr
    password: str

class UserViewModel(Base):
    """Model for viewing user data"""

    username: Optional[str]
    email: EmailStr
    created_at: datetime