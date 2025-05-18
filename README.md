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
#### Docker Start Services:
- Ensure Docker Engine is Running, then-
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
- #### On Windows *(In Cmd Prompt)*
  - POST target_url and secret_key -> returns subscription_id
  ```
  curl -X POST http://localhost:8000/subscriptions/ -H "Content-Type: application/json" -d "{ \"target_url\": \"https://webhook.site/a1c44c41-6367-4e5f-86f0-f18ea75cecb8\", \"secret\": \"secretkey1\" }"
  ```
  - Verify Subscription ID 
  ```
  curl -X GET http://localhost:8000/subscriptions/{subscription_id}
  ```
  - POST Payload to Subscription ID -> returns delivery_id
  ```
  curl -X POST http://localhost:8000/ingest/{subscription_id} -H "Content-Type: application/json" -d "{ \"event\": \"sent_payload\", \"user_id\": 1 }"
  ```
  - GET delivery-status
  ```
  curl -X GET http://localhost:8000/delivery-status/{delivery_id}
  ```
  - GET recent deliveries
  ```
  curl -X GET http://localhost:8000/subscription/{subscription_id}/recent-deliveries
  ```
  - Check cached subscription
  ```
  curl -X GET http://localhost:8000/cache/{subscription_id}
  ```
  - To check Delivery Logs and other DB contents
  ```
  # Locally:
  Ensure Docker is running
  docker exec -it webhook_db psql -U postgres -d Webhook
  \dt
  SELECT * FROM delivery_logs;

  # On Deployed:
  psql installed and added to PATH
  psql postgresql://webhook_delivery_db_user:I7VtJP9zpsvcos4EvVQjxpcLv9QJoi14@dpg-d0g70ii4d50c73fhd7k0-a.oregon-postgres.render.com/webhook_delivery_db
  \dt
  SELECT * FROM delivery_logs;
  ```
  - To Check Cache
  ```
  # Locally:
  Ensure Docker is running
  docker exec -it redis-server redis-cli
  SELECT 2
  GET subscription:{subscription_id}
  ```

  > **Note_1:** To Test Endpoints on Deployed Link- replace `http://localhost:8000` with `https://webhook-delivery.onrender.com` <br>
  > **Note_2:** Postman can also be used for testing, as it provides a better GUI.

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
