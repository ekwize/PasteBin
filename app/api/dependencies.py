from aioredis import Redis
from fastapi import Depends
from app.services.user_service import UserService
from app.services.redis_service import RedisService
from app.services.paste_service import PasteService
from app.repositories.sqlalchemy_repository import SqlAlchemyRepository
from app.repositories.cloud_repository import CloudRepository
from app.core.cache import get_redis_pool


def user_service():
    return UserService(repo=SqlAlchemyRepository)

def redis_service(redis: Redis = Depends(get_redis_pool)):
    return RedisService(redis)

def paste_service():
    return PasteService(db_repo=SqlAlchemyRepository, cloud_repo=CloudRepository)