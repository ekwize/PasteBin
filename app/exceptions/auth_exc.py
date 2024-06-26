from typing import Literal
from fastapi import HTTPException, status


class AuthException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, 
                         detail=self.detail)

## Token exceptions ##

class TokenExpired(AuthException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Token expired"

class TokenAbsentException(AuthException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Token absent"

class IncorrectTokenFormatException(AuthException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Incorrect token format"

class TokenWasNotFound(AuthException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Missing access token"
    
## User Exceptions ##

class UserIsNotPresent(AuthException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="User is not present"

class UserIsNotAuth(AuthException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="User is not auth"

class InvalidUser(AuthException):
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Invalid user"

class UserAlreadyExists(AuthException):
    status_code=status.HTTP_409_CONFLICT 
    detail = "User already exists"

class UserWasNotFound(AuthException):
    status_code=status.HTTP_404_NOT_FOUND
    detail="User was not found"

class IncorrectPassword(AuthException):
    """The exception is due to an incorrect password"""

    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    detail="Incorrect password"

class IncorrectUsernameOrPassword(AuthException):
    """The exception is due to incorrect login information"""
    
    status_code=status.HTTP_401_UNAUTHORIZED 
    detail="Incorrect username or password"

class IncorrectUsername(AuthException):
    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    detail="Incorrect username"

