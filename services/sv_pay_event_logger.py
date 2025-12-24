from sqlalchemy.orm import Session
from models.sv_pay_event import SVPayEvent

def log_event(
    db: Session,
    *,
    intent_id,
    event_type: str,
    metadata: dict | None = None,
):
    """
    Centralized SV Pay event logger.
    Must be used for every intent lifecycle change.
    """

    event = SVPayEvent(
    intent_id=intent_id,
    type=event_type,
    event_metadata=metadata or {},
)


    db.add(event)
    db.commit()
