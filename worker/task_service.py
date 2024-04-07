from aioredis import Redis
from app.core.cache import get_redis_pool
from app.core.database import async_session
from app.models.paste_model import Paste
from app.models.user_model import User #noqa
from sqlalchemy import and_, delete
from datetime import datetime, timedelta
from app.core.cloud import s3, bucket
from app.utils.paste import create_paste_id


class TaskService:
    @staticmethod
    async def delete_expired_paste():
        async with async_session() as session:
            expired_condition = and_(
                Paste.expiration != None,
                Paste.expiration != timedelta(seconds=0),
                Paste.expires_at < datetime.utcnow(), 
            )

            deleted_ids = await session.execute(delete(Paste).where(expired_condition).returning(Paste.id))
            s3.delete_objects(
                Bucket=bucket(),
                Delete={
                    'Objects': [
                        {'Key': str(key)} for key in deleted_ids 
                    ]
                }
            )
            await session.commit()

    @staticmethod
    async def generate_paste_hash():
        redis: Redis = await get_redis_pool()
        await redis.ltrim("hashes", 0, 999)
        length_hashes = len(await redis.lrange("hashes", 0, -1))
            
        while length_hashes < 1000:
            hash = create_paste_id()
            await redis.lpushx("hashes", hash)
            length_hashes += 1