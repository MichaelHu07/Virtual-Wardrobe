import os
from celery import Celery
from app.core.config import settings

# Redis connection
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "tryon_3d_worker",
    broker=redis_url,
    backend=redis_url,
    include=["app.services.tryon_3d.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Worker optimization
    worker_prefetch_multiplier=1, # One task at a time per worker (heavy GPU usage)
    worker_max_tasks_per_child=10, # Restart worker after 10 tasks to prevent leaks
)

