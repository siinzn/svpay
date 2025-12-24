from sqlalchemy.orm import Session
from datetime import datetime, timezone

from models.sv_pay_intent import SVPayIntent
from services.entitlement_service import validate_entitlement
from services.discount_service import calculate_discount
from services.sv_pay_state_machine import transition_sv_pay_intent


def authorize_sv_pay_intent(
    *,
    db: Session,
    intent_id,
):
    """
    Core authorization decision engine.

    Mirrors issuer authorization logic.
    Idempotent by design.
    """

    intent = (
        db.query(SVPayIntent)
        .filter(SVPayIntent.id == intent_id)
        .one_or_none()
    )

    if intent is None:
        raise ValueError("Intent not found")

    # --- Idempotency ---
    if intent.status in {"APPROVED", "DECLINED"}:
        return intent

    if intent.status != "PENDING":
        raise ValueError("Intent not in authorizable state")

    now = datetime.now(timezone.utc)

    # --- Entitlement validation ---
    allowed, reason = validate_entitlement(
        user_id=intent.user_id,
        merchant_id=intent.merchant_id,
        timestamp=now,
    )

    if not allowed:
        return transition_sv_pay_intent(
            db=db,
            intent_id=intent.id,
            new_status="DECLINED",
            reason_code=reason,
            metadata={"decision": "declined"},
        )

    # --- Discount calculation ---
    discount = calculate_discount(
        original_amount=float(intent.original_amount),
        discount_type="percentage",
        discount_value=20,   # example: 20% off
        max_cap=30.00,       # example cap
    )

    intent.discounted_amount = discount["discounted_amount"]
    db.add(intent)
    db.commit()
    db.refresh(intent)

    return transition_sv_pay_intent(
        db=db,
        intent_id=intent.id,
        new_status="APPROVED",
        metadata={
            "decision": "approved",
            "discount": discount,
        },
    )
