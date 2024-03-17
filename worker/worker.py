from celery import Celery

from config import settings
from datetime import timedelta


celery = Celery(
    "tasks",
    broker=settings.build_rabbitmq_dsn(),
    backend=settings.build_celery_redis_dsn(),
    include=["worker.tasks"]
)


celery.conf.beat_schedule = {
    'delete-paste': {
        'task': 'worker.tasks.delete_expired_paste',
        'schedule': timedelta(seconds=15),
    },
    'generate-hash': {
        'task': 'worker.tasks.generate_hash',
        'schedule': timedelta(seconds=10),
    }
}

celery.conf.timezone = 'UTC'
celery.conf.broker_connection_retry_on_startup = True  
