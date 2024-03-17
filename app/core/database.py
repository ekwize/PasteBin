from typing import Any, AsyncGenerator
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from config import settings
from sqlalchemy.orm import declarative_base


if settings.MODE == "TEST":
    DB_URL = settings.build_test_postgres_dsn()
else:
    DB_URL = settings.build_postgres_dsn()


engine = create_async_engine(DB_URL)                           
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

