from fastapi import FastAPI
from app import models
from app.database import engine
from app.routes import router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Webhook Delivery Service",
    description="Manage subscriptions and view webhook delivery logs",
    version="1.0.0"
)
app.include_router(router)