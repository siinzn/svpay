from core.database import SessionLocal
from models.sv_pay_intent import SVPayIntent
from services.sv_pay_state_machine import transition_sv_pay_intent
from datetime import datetime, timedelta, timezone
import uuid

db = SessionLocal()

try:
    intent = SVPayIntent(
        user_id=uuid.uuid4(),
        merchant_id=uuid.uuid4(),
        original_amount=120.00,
        currency="AED",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    db.add(intent)
    db.commit()
    db.refresh(intent)

    transition_sv_pay_intent(db=db, intent_id=intent.id, new_status="APPROVED")
    intent = transition_sv_pay_intent(db=db, intent_id=intent.id, new_status="VOIDED")

    print("Final Status:", intent.status)

finally:
    db.close()
