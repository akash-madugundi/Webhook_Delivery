from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()
redis_broker = os.getenv("REDIS_URL1")
redis_backend = os.getenv("REDIS_URL2")

celery_app = Celery(
    "webhook_delivery",
    broker=redis_broker,
    backend=redis_backend
)

celery_app.conf.update(
    timezone='UTC',
    enable_utc=True,
    beat_schedule={
        'delete-old-delivery-logs-daily': {
            'task': 'app.delivery_tasks.delete_old_logs',
            'schedule': 3600 * 24,  # Every 24 hours
        },
    }
)

import app.delivery_tasks