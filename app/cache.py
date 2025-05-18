import redis
import json
from app.models import Subscription
import os
from dotenv import load_dotenv

redis_url = os.getenv("REDIS_URL")

#! For Deployment
# redis_url = os.getenv("REDIS_URL")

r = redis.from_url(redis_url, decode_responses=True)
# r = redis.Redis(host='redis', port=6379, db=2, decode_responses=True)

def cache_subscription(subscription: Subscription):
    data = {
        "target_url": subscription.target_url,
        "secret": subscription.secret,
    }
    r.setex(f"subscription:{subscription.subscription_id}", 3600, json.dumps(data))  # Cache for 1 hour

def get_cached_subscription(subscription_id: str):
    cached = r.get(f"subscription:{subscription_id}")
    if cached:
        return json.loads(cached)
    return None
