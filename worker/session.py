from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from config import settings



DB_URL = settings.build_postgres_dsn()

engine = create_async_engine(DB_URL)                           
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


    