from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "bot_service",
    broker=settings.RABBITMQ_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    result_expires=3600,
    task_track_started=True,
)

# Ensure the task module is imported so ``llm_request`` is registered and
# does not fail with a KeyError / NotRegistered error.
celery_app.autodiscover_tasks(["app.tasks"])
import app.tasks.llm_tasks  # noqa: E402,F401  (explicit registration)
