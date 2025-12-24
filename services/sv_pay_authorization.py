from sqlalchemy.orm import Session
from models.sv_pay_intent import SVPayIntent
from services.sv_pay_state_machine import transition_sv_pay_intent
from datetime import datetime, timedelta, timezone
import uuid

# 🔧 MOCK entitlement + discount (Milestone 3 simplified)
def validate_entitlement(user_id, merchant_id, timestamp):
    """
    Mock entitlement validation.
    Replace later with real user / offer tables.
    """
    return True, None


def calculate_discount(original_amount):
    """
    Mock discount logic:
    Always 20% off for demo.
    """
    discount = original_amount * 0.2
    return round(original_amount - discount, 2)


def authorize_sv_pay(
    db: Session,
    *,
    user_id,
    merchant_id,
    amount,
    currency
):
    """
    Core SV Pay authorization flow.
    Mirrors real issuer authorization.
    """

    # 1️⃣ Create intent (PENDING)
    intent = SVPayIntent(
        user_id=user_id,
        merchant_id=merchant_id,
        original_amount=amount,
        currency=currency,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )

    db.add(intent)
    db.commit()
    db.refresh(intent)

    # 2️⃣ Idempotency: if already resolved, return it
    if intent.status != "PENDING":
        return intent

    # 3️⃣ Entitlement validation
    allowed, reason = validate_entitlement(
        user_id=user_id,
        merchant_id=merchant_id,
        timestamp=datetime.now(timezone.utc),
    )

    if not allowed:
        return transition_sv_pay_intent(
            db=db,
            intent_id=intent.id,
            new_status="DECLINED",
            reason_code=reason,
        )

    # 4️⃣ Calculate discount
    discounted_amount = calculate_discount(amount)
    intent.discounted_amount = discounted_amount
    db.add(intent)
    db.commit()

    # 5️⃣ Approve intent
    return transition_sv_pay_intent(
        db=db,
        intent_id=intent.id,
        new_status="APPROVED",
        metadata={"discounted_amount": discounted_amount},
    )
