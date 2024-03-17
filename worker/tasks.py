from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .session import async_session_factory
from app.models.paste_model import Paste
from .repository import PasteRepository
from asgiref.sync import async_to_sync
from celery import shared_task
import base64
import secrets
from app.core.cache import get_redis_pool
from config import settings
from aioredis import Redis
from .worker import celery
from app.core.storage import s3
from asyncio import get_event_loop
from logger import logger


async def del_exp_paste():
    paste_repo = PasteRepository(Paste, async_session_factory)
    deleted_ids = await paste_repo.remove_expired_paste()
    for id in deleted_ids:
        s3.delete_object(Bucket='pastes', Key=f'{id[0]}')
    

@shared_task
def delete_expired_paste():
    try:
        loop = get_event_loop()
        loop.run_until_complete(del_exp_paste())
    except Exception as e:
        logger.error(e)
    
  
def create_paste_id() -> str: 
    id = secrets.token_bytes(6)
    hash = base64.urlsafe_b64encode(id)
    unique_id = hash.decode()
    return unique_id 


async def create_paste_hash(): 
    redis: Redis = await get_redis_pool()
    await redis.ltrim("hashes", 0, 999)
    length_hashes = len(await redis.lrange("hashes", 0, -1))
        
    while length_hashes < 1000:
        hash = create_paste_id()
        await redis.lpushx("hashes", hash)
        length_hashes += 1


@shared_task
def generate_hash() -> None:
    try:
        async_to_sync(create_paste_hash)()
    except Exception as e:
        logger.error(e)

    

    