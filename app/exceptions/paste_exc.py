from fastapi import HTTPException, status


class PasteException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self):
        super().__init__(status_code=self.status_code, 
                         detail=self.detail)

class PasteOwnExc(PasteException):
    status_code=status.HTTP_403_FORBIDDEN
    detail="You do not have permission to access this resource"

class PasteWasNotCreated(PasteException):
    detail="Failed to create paste"

class PasteWasNotRemoved(PasteException):
    detail="Failed to remove paste"

class PasteWasNotUpdated(PasteException):
    detail="Failed to update paste"

class PasteWasNotFound(PasteException):
    status_code=status.HTTP_404_NOT_FOUND
    detail="Paste was not found"

class IncorrectPastePassword(PasteException):
    """Paste password verification model"""

    status_code=status.HTTP_403_FORBIDDEN
    detail="Incorrect password"