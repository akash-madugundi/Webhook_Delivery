from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class SubscriptionCreate(BaseModel):
    target_url: HttpUrl
    secret: Optional[str] = None

class SubscriptionUpdate(BaseModel):
    target_url: HttpUrl
    secret: Optional[str] = None

class SubscriptionOut(BaseModel):
    subscription_id: UUID
    target_url: HttpUrl
    secret: Optional[str]

    class Config:
        orm_mode = True

class DeliveryAttempt(BaseModel):
    timestamp: datetime
    attempt_number: int
    outcome: str
    http_status: Optional[int]
    error_details: Optional[str]

class DeliveryStatusResponse(BaseModel):
    delivery_id: str
    subscription_id: str
    target_url: str
    attempts: List[DeliveryAttempt]

class DeliveryLogResponse(BaseModel):
    delivery_id: str
    timestamp: datetime
    attempt_number: int
    outcome: str
    http_status: Optional[int]
    error_details: Optional[str]
    target_url: str