from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Dict, Any

class SVPayEventResponse(BaseModel):
    id: UUID
    intent_id: UUID
    type: str
    metadata: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True
