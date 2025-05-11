import hmac
import hashlib

secret = b'abc123'
payload = b'{"event": "test", "status": "ok"}'

signature = "sha256=" + hmac.new(secret, payload, hashlib.sha256).hexdigest()
print(signature)