from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes.auth_router import router as auth_router
from app.routes.paste_router import router as paste_router
from app.core.cache import get_redis_pool
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = await get_redis_pool()
    FastAPICache.init(RedisBackend(redis), prefix='fastapi-cache')
    yield
    await redis.close()


app = FastAPI(
    title="PasteBin",
    lifespan=lifespan,
)


app.include_router(auth_router)
app.include_router(paste_router)
