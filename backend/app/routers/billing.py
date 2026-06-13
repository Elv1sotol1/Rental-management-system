from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.scheduler import run_billing_cycle
from app.auth import get_current_admin
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/run")
def manual_billing_run(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    charged = run_billing_cycle()
    return {
        "message": "Billing run executed successfully",
        "tenants_charged": charged
    }


@router.get("/logs")
def get_billing_logs(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    from app.models import Invoice
    invoices = db.query(Invoice).order_by(Invoice.created_at.desc()).all()
    return [
        {
            "id": inv.id,
            "tenant_id": inv.tenant_id,
            "amount": inv.amount,
            "billing_period": inv.billing_period,
            "status": inv.status,
            "created_at": inv.created_at
        }
        for inv in invoices
    ]