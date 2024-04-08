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
from app.core.database import engine




@pytest.fixture(autouse=True, scope="session")
async def prepare_db():
    assert settings.MODE == "TEST"
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True, scope="session")
async def redis_session():
    assert settings.MODE == "TEST"
    session = aioredis.from_url(settings.build_test_redis_dsn(), decode_responses=True)
    FastAPICache.init(RedisBackend(session), prefix='fastapi-cache')
    yield session
    await session.close()


@pytest.fixture(autouse=True, scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
