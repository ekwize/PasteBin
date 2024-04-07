from asgiref.sync import async_to_sync
from celery import shared_task
from asyncio import get_event_loop
from logger import logger
from worker.task_service import TaskService

    
@shared_task
def delete_expired_paste():
    try:
        loop = get_event_loop()
        loop.run_until_complete(TaskService.delete_expired_paste())
    except Exception as e:
        logger.error(e)
    

@shared_task
def generate_hash() -> None:
    try:
        async_to_sync(TaskService.generate_paste_hash)()
    except Exception as e:
        logger.error(e)

    

    