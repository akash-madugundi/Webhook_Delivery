from celery import Celery
import os
import ssl
from dotenv import load_dotenv

load_dotenv()
#! For Local
# redis_broker = os.getenv("REDIS_URL")
# redis_backend = os.getenv("REDIS_URL")

redis_url = os.getenv("REDIS_URL")

ssl_options = {
    "ssl_cert_reqs": ssl.CERT_NONE,
    "ssl_check_hostname": False,  # <== this is the fix
}

celery_app = Celery(
    "webhook_delivery",
    broker=redis_url,
    backend=redis_url
)

celery_app.conf.update(
    broker_use_ssl=ssl_options,
    redis_backend_use_ssl=ssl_options,
    timezone='UTC',
    enable_utc=True,
    beat_schedule={
        'delete-old-delivery-logs-daily': {
            'task': 'app.delivery_tasks.delete_old_logs',
            'schedule': 3600 * 24,
        },
    }
)

import app.delivery_tasks