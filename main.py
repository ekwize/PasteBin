import uvicorn
from fastapi import FastAPI
from app.api.routers import routers as api_routers
from app.core.cache import get_redis_pool
from contextlib import asynccontextmanager
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = await get_redis_pool()
    FastAPICache.init(RedisBackend(redis), prefix='fastapi-cache')
    yield
    await redis.close()

def get_app() -> FastAPI:
    app = FastAPI(
        title="PasteBin",
        lifespan=lifespan,
    )
    app.include_router(api_routers)

    return app

app = get_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)