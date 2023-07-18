from celery import Celery
from decouple import config

from services.process_csv import read_csv

celery_app = Celery("tasks", broker=config("RABBIT_URL"), backend="rpc://")


@celery_app.task
def group_file(file: str, task_id: str) -> str:
    return read_csv(file, task_id)
