import uuid
import json
import requests
import hmac
import hashlib
from datetime import datetime, timedelta
from celery import shared_task
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Subscription, DeliveryLog
from app.celery_worker import celery_app

@celery_app.task(bind=True, max_retries=5)
def deliver_webhook(self, subscription_id: str, payload: dict, target_url: str, secret: str, delivery_id: str = None):
    db: Session = SessionLocal()
    attempt_number = self.request.retries + 1
    delivery_id = delivery_id or str(uuid.uuid4())

    try:
        signature = hmac.new(
            key=secret.encode(),
            msg=json.dumps(payload).encode(),
            digestmod=hashlib.sha256
        ).hexdigest()

        headers = {
            "Content-Type": "application/json",
            "X-Hub-Signature-256": f"sha256={signature}"
        }

        response = requests.post(target_url, json=payload, headers=headers, timeout=5)
        success = 200 <= response.status_code < 300
        outcome = "Success" if success else "Failed Attempt"

        log = DeliveryLog(
            delivery_id=delivery_id,
            subscription_id=subscription_id,
            target_url=target_url,
            timestamp=datetime.utcnow(),
            attempt_number=attempt_number,
            outcome=outcome,
            http_status=response.status_code,
            error_details=None if success else f"Non-2xx status: {response.status_code} - {response.text}"
        )
        db.add(log)
        db.commit()

        if not success:
            raise requests.RequestException(f"Non-2xx status: {response.status_code} - {response.text}")

    except Exception as exc:
        db.rollback()  # Important: rollback any partial transaction

        retry_delays = [10, 30, 60, 300, 900]
        retry_delay = retry_delays[self.request.retries] if self.request.retries < len(retry_delays) else 900

        # Recreate the log object for failure (if nothing was logged yet)
        log = DeliveryLog(
            delivery_id=delivery_id,
            subscription_id=subscription_id,
            target_url=target_url,
            timestamp=datetime.utcnow(),
            attempt_number=attempt_number,
            outcome="Failure" if self.request.retries == self.max_retries else "Failed Attempt",
            http_status=None,
            error_details=str(exc)
        )
        db.add(log)
        db.commit()

        raise self.retry(exc=exc, countdown=retry_delay)

    finally:
        db.close()

@celery_app.task()
def delete_old_logs():
    db: Session = SessionLocal()
    retention_cutoff = datetime.utcnow() - timedelta(hours=72)
    deleted = db.query(DeliveryLog).filter(DeliveryLog.created_at < retention_cutoff).delete()
    db.commit()
    db.close()
    print(f"Deleted {deleted} old delivery log(s)")