# test_cache.py
from app.cache import cache_subscription, get_cached_subscription
from app.models import Subscription

def test_cache_roundtrip():
    fake_subscription = Subscription(target_url="https://webhook.site/81ac3c91-dca3-46ed-aa17-191b2ff689f4", secret="key456")
    cache_subscription(fake_subscription)
    
    cached = get_cached_subscription("9722ef74-4d8c-4869-8598-b4982c820dac")
    assert cached["target_url"] == "https://webhook.site/81ac3c91-dca3-46ed-aa17-191b2ff689f4"
    assert cached["secret"] == "mysecretkey"
