import re
from .base_scheme import Base
from pydantic import EmailStr, field_validator
from datetime import datetime
from typing import Optional
from app.exceptions import IncorrectPassword, IncorrectUsername


class UserCreateModel(Base):
    """Model to create user"""

    username: str
    email: EmailStr
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        password_regex = r'^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])[!@#$%^&*(),.?":{}|<>\w-]{8,25}$'

        if not re.fullmatch(password_regex, v):
            raise IncorrectPassword
        return v
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if len(v) < 3:
            raise IncorrectUsername
        return v
    

class UserLoginModel(Base):
    """Model for user authorization"""

    username: str 
    password: str

class UserViewModel(Base):
    """Model for viewing user data"""

    username: Optional[str]
    email: EmailStr
    created_at: datetime
