from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class SVPayIntentBase(BaseModel):
    user_id: UUID
    merchant_id: UUID
    original_amount: float
    currency: str

class SVPayIntentResponse(BaseModel):
    id: UUID
    status: str
    discounted_amount: Optional[float]
    reason_code: Optional[str]
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True
