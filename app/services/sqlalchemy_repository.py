from typing import Type, TypeVar, Optional, Generic

from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base_model import Base
from app.schemas.base_schema import Base as BaseSchema
from .base_repository import AbstractRepository
from app.utils.auth.auth_utils import get_password_hash


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseSchema)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseSchema)


class SqlAlchemyRepository(AbstractRepository, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):

    def __init__(self, model: Type[ModelType], db_session: AsyncSession):
        self._async_session = db_session
        self.model = model

    async def create(self, data: CreateSchemaType) -> ModelType:
        async with self._async_session as session:
            instance = self.model(**data.model_dump())
            
            if instance.password:
                instance.password = get_password_hash(instance.password)


            session.add(instance)
            await session.commit()
            await session.refresh(instance)
            return instance

    async def update(self, data: UpdateSchemaType, **filters) -> ModelType:
        async with self._async_session as session:
            if data.password:
                data.password = get_password_hash(data.password)
            
            stmt = update(self.model).values(**data.model_dump()).filter_by(**filters).returning(self.model)
            res = await session.execute(stmt)
            await session.commit()
            return res.scalar_one()

    async def delete(self, **filters) -> None:
        async with self._async_session as session:
            await session.execute(delete(self.model).filter_by(**filters))
            await session.commit()

    async def get_single(self, **filters) -> Optional[ModelType] | None:
        async with self._async_session as session:
            row = await session.execute(select(self.model).filter_by(**filters))
            return row.scalar_one_or_none()
        
    async def get_all(self, **filters) -> list[ModelType] | None:
        async with self._async_session as session:
            rows = await session.execute(select(self.model).filter_by(**filters))
            return rows.scalars().all()

    async def get_multi(
            self,
            order: str = "id",
            limit: int = 100,
            offset: int = 0
    ) -> list[ModelType]:
        async with self._async_session as session:
            stmt = select(self.model).order_by(*order).limit(limit).offset(offset)
            row = await session.execute(stmt)
            return row.scalars().all()
        