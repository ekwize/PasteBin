import calendar
from typing import Literal, Optional
from app.schemas.base_scheme import Base
from uuid import UUID
from datetime import datetime, timedelta
from app.models.user_model import PortalRole
from pydantic import field_validator


class PasteModel(Base):
    id: str
    user_id: Optional[UUID] 
    username: Optional[str] 
    role: PortalRole
    text: str
    title: Optional[str] 
    category: Optional[str] 
    password: Optional[str]
    exposure: Optional[Literal["Public", "Private"]] 
    expiration: Optional[timedelta] 
    expires_at: Optional[datetime] 
    created_at: Optional[datetime] 
    updated_at: Optional[datetime] 


class PasteForUserModel(Base):
    """Model that is given to the user to create paste"""

    text: str
    title: Optional[str] = "Untitled"
    category: Optional[str] 
    password: Optional[str] 
    exposure: Optional[Literal["Public", "Private"]] 
    expiration: Optional[
        Literal[
            "Never", 
            "Burn after read", 
            "10 Minutes", 
            "1 Day", 
            "2 Days", 
            "1 Week", 
            "1 Month", 
            "1 Year"
        ]
    ] 

    @field_validator("title", "category", "password")
    @classmethod
    def validate(cls, v):
        if v != None and len(v.strip()) == 0:
            raise ValueError("Field cannot be empty")
        return v

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str):
        if len(v.strip()) == 0:
            raise ValueError("Text cannot be empty")
        return v


    @field_validator("expiration")
    @classmethod
    def validate_expiration(cls, v: str) -> timedelta:
        try:
            now = datetime.now()
            month = now.month
            year = now.year
            days_in_month = calendar.monthrange(year, month)[1]
            
            expiration_delta = {
                "Never": None,
                "Burn after read": timedelta(seconds=0),
                "10 Minutes": timedelta(minutes=10), 
                "1 Day": timedelta(days=1), 
                "2 Days": timedelta(days=2), 
                "1 Week": timedelta(weeks=1), 
                "1 Month": timedelta(days=days_in_month), 
                "1 Year": timedelta(days=365)
            }
            return expiration_delta[v]
        except:
            raise ValueError("Invalid Expiration")


class PasteCreateModel(Base):
    """Model for saving the created paste to the database"""

    id: str
    user_id: Optional[UUID] = None
    username: Optional[str] = None
    role: PortalRole
    title: Optional[str] = "Untitled"
    category: Optional[str] = None
    password: Optional[str] = None
    exposure: Optional[Literal["Public", "Private"]] = "Public"
    expiration: Optional[timedelta] = None
    expires_at: Optional[datetime] = None

class PasteViewModel(Base):
    """Model to view paste"""

    id: str
    text: str
    username: Optional[str]
    title: Optional[str] 
    category: Optional[str] 
    exposure: Optional[Literal["Public", "Private"]] 
    expiration: Optional[timedelta] 
    expires_at: Optional[datetime]
    created_at: datetime

class PasteAuthModel(Base):
    """Model that authenticates you to access the paste"""

    id: str
    password: Optional[str]
        
class PasteUpdateModel(Base):
    """Model to update the data"""

    title: Optional[str] = "Untitled"
    category: Optional[str] = None
    password: Optional[str] = None
    exposure: Optional[Literal["Public", "Private"]] 
    expiration: Optional[timedelta] 
    expires_at: Optional[datetime] 
