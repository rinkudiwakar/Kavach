# backend/celery_worker.py
from celery import Celery
from configs.settings import settings

celery_app = Celery(
    "voice_system",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Optional: task serialization / time limits can be set here
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]
