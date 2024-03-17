from functools import wraps
from app.models.user_model import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.sqlalchemy_repository import SqlAlchemyRepository
from app.exceptions import PasteOwnExc, UserIsNotAuth 
from app.models.paste_model import Paste

def isOwner(func):
    @wraps(func)
    async def has_permissions(paste_id: str, current_user: User, session: AsyncSession, *args, **kwargs):
        if not current_user:
            raise UserIsNotAuth
    
        paste_repo = SqlAlchemyRepository(Paste, session)
        paste = await paste_repo.get_single(id=paste_id)

        if current_user.id != paste.user_id:
            raise PasteOwnExc
        
        return await func(paste_id, current_user, session, *args, **kwargs)
    
    return has_permissions

            
