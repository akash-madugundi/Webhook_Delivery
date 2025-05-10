from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from app.database import Base
import uuid
from sqlalchemy.orm import relationship
from datetime import datetime

class Subscription(Base):
    __tablename__ = "subscriptions"
    subscription_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    target_url = Column(String, nullable=False)
    secret = Column(String, nullable=True)

class DeliveryLog(Base):
    __tablename__ = "delivery_logs"

    id = Column(Integer, primary_key=True, index=True)
    delivery_id = Column(String, index=True)
    subscription_id = Column(String, ForeignKey("subscriptions.subscription_id"))
    target_url = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    attempt_number = Column(Integer)
    outcome = Column(String)
    http_status = Column(Integer, nullable=True)
    error_details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    subscription = relationship("Subscription")