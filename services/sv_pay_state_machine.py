from sqlalchemy.orm import Session
from models.sv_pay_intent import SVPayIntent
from services.sv_pay_event_logger import log_event
from datetime import datetime, timezone

# ----------------------------------------
# Allowed state transitions
# ----------------------------------------

ALLOWED_TRANSITIONS = {
    "PENDING": {"APPROVED", "DECLINED", "EXPIRED"},
    "APPROVED": {"USED", "VOIDED", "EXPIRED"},
}

# Terminal states are immutable forever
TERMINAL_STATES = {"DECLINED", "USED", "VOIDED", "EXPIRED"}


def can_transition(from_status: str, to_status: str) -> bool:
    """
    Pure function.
    Determines whether a state transition is allowed.

    No database access.
    No side effects.
    """

    # Terminal states cannot transition at all
    if from_status in TERMINAL_STATES:
        return False

    # Unknown states are rejected defensively
    if from_status not in ALLOWED_TRANSITIONS:
        return False

    return to_status in ALLOWED_TRANSITIONS[from_status]

def transition_sv_pay_intent(
    db: Session,
    *,
    intent_id,
    new_status: str,
    reason_code: str | None = None,
    metadata: dict | None = None,
):
    """
    Atomically transitions an SV Pay intent to a new state.

    Guarantees:
    - Valid transition
    - Single commit
    - Event always logged
    """

    # 1. Load intent
    intent = (
        db.query(SVPayIntent)
        .filter(SVPayIntent.id == intent_id)
        .one_or_none()
    )

    if intent is None:
        raise ValueError("SV Pay intent not found")

    # 2. Validate transition
    if not can_transition(intent.status, new_status):
        raise ValueError(
            f"Illegal SV Pay transition: {intent.status} → {new_status}"
        )

    # 3. Apply transition
    intent.status = new_status

    if reason_code:
        intent.reason_code = reason_code

    # 4. Persist intent + event atomically
    db.add(intent)

    log_event(
        db=db,
        intent_id=intent.id,
        event_type=_map_status_to_event(new_status),
        metadata=metadata or {},
    )

    db.commit()
    db.refresh(intent)

    return intent

def _map_status_to_event(status: str) -> str:
    """
    Maps intent status transitions to SV Pay event types.
    Keeps issuer-style parity.
    """

    return {
        "APPROVED": "AUTH_APPROVED",
        "DECLINED": "AUTH_DECLINED",
        "USED": "USED",
        "VOIDED": "VOIDED",
        "EXPIRED": "EXPIRED",
    }[status]


def expire_eligible_intents(db: Session):
    """
    Marks expired SV Pay intents.

    Rules:
    - Only PENDING and APPROVED can expire
    - Uses expires_at timestamp
    """

    now = datetime.now(timezone.utc)


    intents = (
        db.query(SVPayIntent)
        .filter(
            SVPayIntent.status.in_(["PENDING", "APPROVED"]),
            SVPayIntent.expires_at <= now,
        )
        .all()
    )

    for intent in intents:
        transition_sv_pay_intent(
            db=db,
            intent_id=intent.id,
            new_status="EXPIRED",
            reason_code="intent_expired",
            metadata={"expired_at": now.isoformat()},
        )
