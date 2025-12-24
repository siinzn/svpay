from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import SessionLocal
from schemas.sv_pay_api import (
    SVPayAuthorizeRequest,
    SVPayAuthorizeResponse,
    SVPayActionRequest,
    SVPayActionResponse,
)
from services.sv_pay_authorization import authorize_sv_pay
from services.sv_pay_state_machine import transition_sv_pay_intent
from models.sv_pay_intent import SVPayIntent

router = APIRouter(prefix="/svpay", tags=["SV Pay"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------- AUTHORIZE ----------

@router.post("/authorize", response_model=SVPayAuthorizeResponse)
def authorize_svpay(
    payload: SVPayAuthorizeRequest,
    db: Session = Depends(get_db),
):
    intent = authorize_sv_pay(
        db=db,
        user_id=payload.user_id,
        merchant_id=payload.merchant_id,
        amount=payload.amount,
        currency=payload.currency,
    )

    return SVPayAuthorizeResponse(
        intent_id=intent.id,
        status=intent.status,
        original_amount=float(intent.original_amount),
        discounted_amount=float(intent.discounted_amount)
        if intent.discounted_amount
        else None,
        reason_code=intent.reason_code,
    )


# ---------- CONFIRM ----------

@router.post("/confirm", response_model=SVPayActionResponse)
def confirm_svpay(
    payload: SVPayActionRequest,
    db: Session = Depends(get_db),
):
    intent = db.query(SVPayIntent).get(payload.intent_id)

    if not intent or intent.status != "APPROVED":
        raise HTTPException(status_code=400, detail="Intent not approvable")

    intent = transition_sv_pay_intent(
        db=db,
        intent_id=payload.intent_id,
        new_status="USED",
    )

    return SVPayActionResponse(intent_id=intent.id, status=intent.status)


# ---------- VOID ----------

@router.post("/void", response_model=SVPayActionResponse)
def void_svpay(
    payload: SVPayActionRequest,
    db: Session = Depends(get_db),
):
    intent = db.query(SVPayIntent).get(payload.intent_id)

    if not intent or intent.status != "APPROVED":
        raise HTTPException(status_code=400, detail="Intent not voidable")

    intent = transition_sv_pay_intent(
        db=db,
        intent_id=payload.intent_id,
        new_status="VOIDED",
    )

    return SVPayActionResponse(intent_id=intent.id, status=intent.status)
