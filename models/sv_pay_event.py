import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from core.database import Base

class SVPayEvent(Base):
    __tablename__ = "sv_pay_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    intent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sv_pay_intents.id", ondelete="CASCADE"),
        nullable=False,
    )

    type = Column(
        Enum(
            "AUTH_APPROVED",
            "AUTH_DECLINED",
            "USED",
            "VOIDED",
            "EXPIRED",
            name="sv_pay_event_type",
        ),
        nullable=False,
    )

    event_metadata = Column("metadata", JSONB, nullable=False, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
