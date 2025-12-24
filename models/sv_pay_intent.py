import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Enum, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from core.database import Base

class SVPayIntent(Base):
    __tablename__ = "sv_pay_intents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    merchant_id = Column(UUID(as_uuid=True), nullable=False)

    original_amount = Column(Numeric(10, 2), nullable=False)
    discounted_amount = Column(Numeric(10, 2))

    currency = Column(String(3), nullable=False)

    status = Column(
        Enum(
            "PENDING",
            "APPROVED",
            "DECLINED",
            "USED",
            "VOIDED",
            "EXPIRED",
            name="sv_pay_intent_status",
        ),
        nullable=False,
        default="PENDING",
    )

    reason_code = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)
