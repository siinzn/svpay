from core.database import SessionLocal
from models.sv_pay_intent import SVPayIntent
from services.sv_pay_state_machine import transition_sv_pay_intent
from datetime import datetime, timedelta, timezone
import uuid

db = SessionLocal()

try:
    # 1️⃣ Create a new intent (PENDING)
    intent = SVPayIntent(
        user_id=uuid.uuid4(),
        merchant_id=uuid.uuid4(),
        original_amount=100.00,
        currency="AED",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )

    db.add(intent)
    db.commit()
    db.refresh(intent)

    print("Created intent:")
    print(intent.id, intent.status)

    # 2️⃣ Approve the intent
    intent = transition_sv_pay_intent(
        db=db,
        intent_id=intent.id,
        new_status="APPROVED",
        metadata={"manual_test": True},
    )

    print("After approval:")
    print(intent.id, intent.status)

    # 3️⃣ Mark intent as USED
    intent = transition_sv_pay_intent(
        db=db,
        intent_id=intent.id,
        new_status="USED",
        metadata={"manual_test": True},
    )

    print("After use:")
    print(intent.id, intent.status)

    # 4️⃣ Try illegal transition (SHOULD FAIL)
    print("Attempting illegal transition...")
    transition_sv_pay_intent(
        db=db,
        intent_id=intent.id,
        new_status="APPROVED",
    )

except Exception as e:
    print("ERROR (expected for illegal transition):")
    print(e)

finally:
    db.close()
