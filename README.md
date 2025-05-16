# Webhook Delivery Service

A robust backend system for managing webhook subscriptions, ingesting and delivering webhooks asynchronously with retries, signature verification, logging, caching, and status tracking.

#### 🌐 Live Demo - [Backend Service](https://webhook-delivery.onrender.com/docs)

---

## Features
  * Subscription Management (CRUD)
  * Asynchronous Webhook Ingestion and Delivery
  * HMAC-SHA256 Signature Verification
  * Delivery Logging with Retry (Exponential Backoff)
  * Caching with Redis (Upstash)
  * Log Retention Cleanup
  * Status & Analytics Endpoints
  * Dockerized (with docker-compose)
  * Deployed on Render + Upstash
  * Swagger UI for API interaction

> ⚠️ **Note:** *Retrieving of data from database may take some time(<=50 sec) as it's a free service.*

---

## Installation & Setup
### Prerequisites (for local running)
- Docker Installed
- Python-3.12

### Steps to Run Locally
#### Clone the Repository
```bash
git clone <repository-url>
cd Webhook_Delivery
```
#### Create a Virtual Environment
```bash
python -m venv .webhook
.webhook\Scripts\activate  # On Windows
# OR
source .webhook/bin/activate  # On Unix/Mac
```
#### Install requirements:
```
pip install -r requirements.txt
```
#### Set up environment variables (.env file):
```bash
DATABASE_URL = postgresql://webhook_delivery_db_user:I7VtJP9zpsvcos4EvVQjxpcLv9QJoi14@dpg-d0g70ii4d50c73fhd7k0-a.oregon-postgres.render.com/webhook_delivery_db
REDIS_URL=rediss://:AT31AAIjcDEyNzliYzM3NWE5MmE0MWFkYTdhOTgxYzlmOGUxNmViN3AxMA@solid-baboon-15861.upstash.io
```
#### Docker Start Services:
```
docker-compose up --build 
```
#### Docker Stop Services:
```
docker-compose down -v
```

---

## Technologies Stack
  - **Backend**: FastAPI
  - **ORM**: SQLAlchemy
  - **Database**: PostgreSQL (Render)
  - **Cache & Queue Broker**: Redis (Upstash)
  - **Async Workers**: Celery + Celery Beat
  - **Containerization**: Docker + Docker Compose
  - **Testing**: Postman/ Command Prompt

---

## API Usage Examples
- *refer to-* [https://webhook-delivery.onrender.com/docs]
- #### On Windows (cmd prompt)
  - POST target_url and secret_key -> returns subscription_id
  ```
  curl -X POST https://webhook-delivery.onrender.com/subscriptions/ -H "Content-Type: application/json" -d "{ \"target_url\": \"https://webhook.site/81ac3c91-dca3-46ed-aa17-191b2ff689f4\", \"secret\": \"secretkey1\" }"
  ```
  - Verify Subscription ID 
  ```
  curl -X GET https://webhook-delivery.onrender.com/subscriptions/a2fede6b-2eb6-4336-bb1a-3c7e0d2d0e3b
  ```
  - POST Payload to Subscription ID -> returns delivery_id
  ```
  curl -X POST https://webhook-delivery.onrender.com/ingest/a2fede6b-2eb6-4336-bb1a-3c7e0d2d0e3b -H "Content-Type: application/json" -d "{ \"event\": \"sent_payload\", \"user_id\": 1 }"
  ```
  - GET delivery-status
  ```
  curl -X GET https://webhook-delivery.onrender.com/subscription/a2fede6b-2eb6-4336-bb1a-3c7e0d2d0e3b/recent-deliveries
  ```
  - Check cached subscription
  ```
  curl -X GET https://webhook-delivery.onrender.com/cache/a2fede6b-2eb6-4336-bb1a-3c7e0d2d0e3b
  ```
---

## Architecture Highlights
  - Framework: FastAPI
    - Fast performance with async support
    - Built-in OpenAPI/Swagger for easy testing
    - Clean dependency injection system
  - Database: PostgreSQL (on Render)
    - Strong consistency and relational integrity
    - Delivery logs, subscriptions, and retry tracking require structured schema
  - Async Queue: Celery + Redis (Upstash)
    - Celery workers process webhook deliveries in the background
    - Redis serves as both broker and cache
    - Celery Beat schedules cleanup tasks (e.g., log retention)
  - Retry Strategy
    - Max 5 retries per delivery
    - Exponential backoff: 10s → 30s → 1m → 5m → 15m
    - Failures logged with error reasons
  - Others
    - Signature Verification: The service includes X-Hub-Signature-256: sha256=... in the outbound request.
    - Log Retention: A periodic task via Celery Beat cleans up old logs automatically (stored for 72hrs).
    
---

## Assumptions
- Ingestion clients trust the response 202 Accepted and will not retry from their end.
- Subscriptions are pre-created via API before ingestion is attempted.
- Redis is available and accessible via provided URL (Upstash or local Docker).

---

## Estimated Monthly Cost (Free Tier)
  | Service         | Provider | Usage Assumption                        | Estimated Monthly Cost     |
  | --------------- | -------- | --------------------------------------- | -------------------------- |
  | Redis (Upstash) | Upstash  | 5000 webhooks/day → \~6000 requests/day | \~\$1 (within free limits) |
  | PostgreSQL      | Render   | \~150k delivery log rows/month          | Free (Starter tier)        |
  | App Hosting     | Render   | 24x7 Uvicorn on Render                  | Free (Web Services)        |
 
  Total: ≈ $1/month
