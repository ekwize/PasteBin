import asyncio
import aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from httpx import AsyncClient
import pytest
from config import settings
from app.models.base_model import Base
from main import app
from config import settings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def engine():
    assert settings.MODE == "TEST"
    return create_async_engine(settings.build_test_postgres_dsn())


@pytest.fixture(scope="session")
async def tables(engine):
    assert settings.MODE == "TEST"
    await Base.metadata.create_all(engine)
    yield 
    await Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(engine: AsyncEngine, tables):
    connection = engine.connect()
    session = AsyncSession(bind=connection)

    yield session

    session.close()
    connection.close()


@pytest.fixture(scope="session")
async def redis_session():
    assert settings.MODE == "TEST"
    session = aioredis.from_url(settings.build_test_redis_dsn(), decode_responses=True)
    FastAPICache.init(RedisBackend(session), prefix='fastapi-cache')
    yield session
    await session.close()


@pytest.fixture(scope="function")
async def ac():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
async def authenticated_ac():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await ac.post("/auth/login", json={
            "email": "il@example.com",
            "password": "Password123",
        })
        assert ac.cookies["access_token"]
        yield ac