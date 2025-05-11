# Webhook Delivery Service

A robust backend system for managing webhook subscriptions, ingesting and delivering webhooks asynchronously with retries, signature verification, logging, caching, and status tracking.

#### 🌐 Live Demo - [Backend Service]([https://newshub-c5r7.onrender.com](https://webhook-delivery.onrender.com/docs))

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
DATABASE_URL=(your_db_url)
REDIS_URL=(your_redis_url)
```

#### Docker Start Services:
```
docker-compose up build 
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
- *refer to-* https://newshub-c5r7.onrender.com](https://webhook-delivery.onrender.com/docs

---

## Signature Verification
- If a secret is set for a subscription:
  - The service includes X-Hub-Signature-256: sha256=... in the outbound request.
  - Incoming payloads (for verification-enabled subscriptions) are rejected with 401 Unauthorized if signature mismatch occurs.

---

## Log Retention
- Delivery logs are stored for 72 hours.
- A periodic task via Celery Beat cleans up old logs automatically.

---

## Architecture Highlights
- FastAPI was chosen for high performance and async capability.
- Celery for background job processing and retries.
- Upstash Redis is used for both caching and message brokering (serverless, low-latency).
- PostgreSQL via Render for reliability and relational consistency.
- Docker Compose enables simple, isolated local development.

- Architecture Choices Explained
🔧 Framework: FastAPI
Fast performance with async support
Built-in OpenAPI/Swagger for easy testing
Clean dependency injection system

🧱 Database: PostgreSQL (on Render)
Strong consistency and relational integrity
Delivery logs, subscriptions, and retry tracking require structured schema

🔁 Async Queue: Celery + Redis (Upstash)
Celery workers process webhook deliveries in the background
Redis serves as both broker and cache
Celery Beat schedules cleanup tasks (e.g., log retention)

🔁 Retry Strategy
Max 5 retries per delivery
Exponential backoff: 10s → 30s → 1m → 5m → 15m
Failures logged with error reasons

---

## Assumptions
- Ingestion clients trust the response 202 Accepted and will not retry from their end.
- Subscriptions are pre-created via API before ingestion is attempted.
- Redis is available and accessible via provided URL (Upstash or local Docker).

---

## Estimated Monthly Cost (Free Tier)

