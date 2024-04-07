from aioredis import Redis
from app.utils.paste import create_paste_id
from logger import logger


class RedisService:
    def __init__(self, redis: Redis):
        self.redis: Redis = redis

    async def get_hash(self):
        paste_id = await self.redis.rpop("hashes")
        
        if not paste_id:
            paste_id = create_paste_id()
            logger.info(
                msg="No hash in the 'hashes'"
            )
        return paste_id
    
    async def get(self, name: str):
        return await self.redis.get(name)
    
    async def set(self, name: str, value: str, ex: int):
        await self.redis.set(name, value, ex)
    
    async def delete(self, name: str):
        await self.redis.delete(name)
