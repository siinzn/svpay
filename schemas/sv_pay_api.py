from pydantic import BaseModel
from uuid import UUID
from typing import Optional

# ---------- AUTHORIZE ----------

class SVPayAuthorizeRequest(BaseModel):
    user_id: UUID
    merchant_id: UUID
    amount: float
    currency: str = "AED"


class SVPayAuthorizeResponse(BaseModel):
    intent_id: UUID
    status: str
    original_amount: float
    discounted_amount: Optional[float] = None
    reason_code: Optional[str] = None


# ---------- CONFIRM / VOID ----------

class SVPayActionRequest(BaseModel):
    intent_id: UUID


class SVPayActionResponse(BaseModel):
    intent_id: UUID
    status: str
