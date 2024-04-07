import aioredis
from aioredis import Redis
from config import settings


if settings.MODE == "TEST":
    REDIS_URL = settings.build_test_redis_dsn()
else:
    REDIS_URL = settings.build_app_redis_dsn()


async def get_redis_pool() -> Redis: 
    session = aioredis.from_url(REDIS_URL, decode_responses=True)
    return session
    
