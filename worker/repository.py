from sqlalchemy import and_, delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from typing import TypeVar, Type
from app.models.base_model import Base
from datetime import datetime
from app.models.user_model import User #noqa



ModelType = TypeVar("ModelType", bound=Base)


class PasteRepository:
     
    def __init__(self, model: Type[ModelType], db_session: async_sessionmaker[AsyncSession]):
        self._async_session = db_session
        self.model = model

    async def remove_expired_paste(self) -> None:
        async with self._async_session() as session:

            expired_condition = and_(
                self.model.expiration != None,
                self.model.expiration != 0,
                self.model.expires_at < datetime.utcnow(), 
            )

            deleted_ids = await session.execute(delete(self.model).where(expired_condition).returning(self.model.id))
            await session.commit()

            return deleted_ids.fetchall()