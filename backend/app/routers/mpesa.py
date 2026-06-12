from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import Tenant, Payment, PaymentMethod, PaymentStatus
from app.services.mpesa_service import stk_push
from app.auth import get_current_admin
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class STKPushRequest(BaseModel):
    tenant_id: int
    amount: int


@router.post("/stk-push")
def initiate_stk_push(
    payload: STKPushRequest,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    tenant = db.query(Tenant).filter(Tenant.id == payload.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    try:
        response = stk_push(
            phone_number=tenant.phone_number,
            amount=payload.amount,
            account_ref=f"Unit-{tenant.unit_id}"
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"M-Pesa request failed: {str(e)}")

    if response.get("ResponseCode") != "0":
        raise HTTPException(
            status_code=400,
            detail=response.get("errorMessage", "STK Push failed")
        )

    # Create a pending payment record
    pending = Payment(
        tenant_id=tenant.id,
        amount=payload.amount,
        phone_number=tenant.phone_number,
        payment_method=PaymentMethod.mpesa,
        status=PaymentStatus.pending
    )
    db.add(pending)
    db.commit()
    db.refresh(pending)

    return {
        "message": "STK Push sent successfully",
        "payment_id": pending.id,
        "checkout_request_id": response.get("CheckoutRequestID")
    }


@router.post("/callback")
async def mpesa_callback(request: Request, db: Session = Depends(get_db)):
    try:
        body = await request.json()
        logger.info(f"M-Pesa callback received: {body}")

        stk_callback = body.get("Body", {}).get("stkCallback", {})
        result_code = stk_callback.get("ResultCode")
        result_desc = stk_callback.get("ResultDesc")

        if result_code != 0:
            logger.warning(f"STK Push failed or cancelled: {result_desc}")
            return {"ResultCode": 0, "ResultDesc": "Accepted"}

        # Parse the metadata items
        items = stk_callback.get("CallbackMetadata", {}).get("Item", [])
        metadata = {item["Name"]: item.get("Value") for item in items}

        receipt_number = metadata.get("MpesaReceiptNumber")
        amount = metadata.get("Amount")
        phone_raw = str(metadata.get("PhoneNumber", ""))

        # Generate phone number variants for matching
        variants = []
        if phone_raw.startswith("254"):
            variants = [phone_raw, "+" + phone_raw, "0" + phone_raw[3:]]
        elif phone_raw.startswith("+254"):
            variants = [phone_raw, phone_raw[1:], "0" + phone_raw[4:]]
        elif phone_raw.startswith("0"):
            variants = [phone_raw, "254" + phone_raw[1:], "+254" + phone_raw[1:]]

        # Check for duplicate receipt
        existing = db.query(Payment).filter(
            Payment.mpesa_receipt_number == receipt_number
        ).first()
        if existing:
            logger.warning(f"Duplicate receipt ignored: {receipt_number}")
            return {"ResultCode": 0, "ResultDesc": "Accepted"}

        # Find matching tenant
        tenant = None
        for variant in variants:
            tenant = db.query(Tenant).filter(
                Tenant.phone_number == variant
            ).first()
            if tenant:
                break

        if not tenant:
            logger.warning(f"No tenant found for phone variants: {variants}")
            return {"ResultCode": 0, "ResultDesc": "Accepted"}

        # Update tenant balance and log payment
        tenant.balance -= float(amount)

        payment = Payment(
            tenant_id=tenant.id,
            mpesa_receipt_number=receipt_number,
            amount=float(amount),
            phone_number=phone_raw,
            payment_method=PaymentMethod.mpesa,
            status=PaymentStatus.confirmed
        )
        db.add(payment)
        db.commit()

        logger.info(f"Payment confirmed for {tenant.name} — KES {amount} — Receipt {receipt_number}")
        return {"ResultCode": 0, "ResultDesc": "Accepted"}

    except Exception as e:
        logger.error(f"Callback processing error: {str(e)}")
        return {"ResultCode": 0, "ResultDesc": "Accepted"}