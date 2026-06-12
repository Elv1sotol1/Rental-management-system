from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Payment, Tenant, PaymentMethod, PaymentStatus
from app.schemas import ManualPaymentCreate, PaymentResponse
from app.auth import get_current_admin

router = APIRouter()


@router.post("/manual", response_model=PaymentResponse)
def record_manual_payment(
    payload: ManualPaymentCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    tenant = db.query(Tenant).filter(Tenant.id == payload.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    payment = Payment(
        tenant_id=tenant.id,
        amount=payload.amount,
        payment_method=PaymentMethod.cash,
        status=PaymentStatus.confirmed
    )
    tenant.balance -= payload.amount
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


@router.get("/", response_model=List[PaymentResponse])
def get_payments(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    return db.query(Payment).order_by(Payment.timestamp.desc()).all()