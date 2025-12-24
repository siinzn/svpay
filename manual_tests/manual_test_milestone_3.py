from core.database import SessionLocal
from models.sv_pay_intent import SVPayIntent
from services.authorization_service import authorize_sv_pay_intent
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

    print("Created intent:", intent.status)

    intent = authorize_sv_pay_intent(db=db, intent_id=intent.id)

    print("After authorization:")
    print("Status:", intent.status)
    print("Discounted amount:", intent.discounted_amount)

except Exception as e:
    print("ERROR:", e)

finally:
    db.close()
