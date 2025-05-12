from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Subscription, DeliveryLog
from app import schemas
import hmac
import hashlib
import requests
import json
from app.delivery_tasks import deliver_webhook
from app.schemas import DeliveryStatusResponse, DeliveryLogResponse
from app.cache import get_cached_subscription, cache_subscription
from app.cache import r
from uuid import uuid4

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/subscriptions/", response_model=schemas.SubscriptionOut)
def create_subscription(data: schemas.SubscriptionCreate, db: Session = Depends(get_db)):
    subscription = Subscription(target_url=str(data.target_url), secret=data.secret)
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription

@router.get("/subscriptions/{subscription_id}", response_model=schemas.SubscriptionOut)
def get_subscription(subscription_id: str, db: Session = Depends(get_db)):
    subscription = db.query(Subscription).filter_by(subscription_id=subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return subscription

@router.put("/subscriptions/{subscription_id}", response_model=schemas.SubscriptionOut)
def update_subscription(subscription_id: str, data: schemas.SubscriptionUpdate, db: Session = Depends(get_db)):
    subscription = db.query(Subscription).filter_by(subscription_id=subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    subscription.target_url = str(data.target_url)
    subscription.secret = data.secret
    db.commit()
    db.refresh(subscription)
    return subscription

@router.delete("/subscriptions/{subscription_id}")
def delete_subscription(subscription_id: str, db: Session = Depends(get_db)):
    subscription = db.query(Subscription).filter_by(subscription_id=subscription_id).first()
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    db.delete(subscription)
    db.commit()
    return {"message": "Subscription deleted"}

@router.post("/ingest/{subscription_id}", status_code=202)
async def ingest_webhook(subscription_id: str, request: Request, db: Session = Depends(get_db)):
    subscription_data = get_cached_subscription(subscription_id)

    if not subscription_data:
        subscription = db.query(Subscription).filter_by(subscription_id=subscription_id).first()
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        cache_subscription(subscription)
        subscription_data = {"target_url": subscription.target_url, "secret": subscription.secret}

    payload_dict = await request.json()
    delivery_id = str(uuid4())

    deliver_webhook.apply_async(kwargs={
        "subscription_id": subscription_id,
        "payload": payload_dict,
        "target_url": subscription_data["target_url"],
        "secret": subscription_data["secret"],
        "delivery_id": delivery_id
    })

    return {
        "message": f"Accepted for asynchronous processing. Note this delivery_id to query delivery status.",
        "delivery_id": delivery_id
    }
    

@router.get("/delivery-status/{delivery_id}", response_model=DeliveryStatusResponse)
def get_delivery_status(delivery_id: str, db: Session = Depends(get_db)):
    delivery = db.query(DeliveryLog).filter(DeliveryLog.delivery_id == delivery_id).order_by(DeliveryLog.attempt_number).all()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery ID not found")

    return {
        "delivery_id": delivery_id,
        "subscription_id": delivery[0].subscription_id,
        "target_url": delivery[0].target_url,
        "attempts": [{
            "timestamp": log.timestamp,
            "attempt_number": log.attempt_number,
            "outcome": log.outcome,
            "http_status": log.http_status,
            "error_details": log.error_details,
        } for log in delivery]
    }

@router.get("/subscription/{subscription_id}/recent-deliveries", response_model=list[DeliveryLogResponse])
def get_recent_deliveries(subscription_id: str, db: Session = Depends(get_db)):
    deliveries = db.query(DeliveryLog).filter_by(subscription_id=subscription_id).order_by(DeliveryLog.timestamp.desc()).limit(20).all()
    return [{
        "delivery_id": log.delivery_id,
        "timestamp": log.timestamp,
        "attempt_number": log.attempt_number,
        "outcome": log.outcome,
        "http_status": log.http_status,
        "error_details": log.error_details,
        "target_url": log.target_url,
    } for log in deliveries]

@router.get("/cache/{subscription_id}")
def check_cache(subscription_id: str):
    cached = r.get(f"subscription:{subscription_id}")
    if not cached:
        return {"cached": False}
    return {"cached": True, "data": json.loads(cached)}
