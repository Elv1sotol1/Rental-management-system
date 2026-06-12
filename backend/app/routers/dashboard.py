from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Unit, Tenant, Payment, UnitStatus, TenantStatus, PaymentStatus
from app.schemas import DashboardResponse
from app.auth import get_current_admin

router = APIRouter()


@router.get("/", response_model=DashboardResponse)
def get_dashboard(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    total_units = db.query(Unit).filter(Unit.status != UnitStatus.inactive).count()

    occupied_units = db.query(Tenant).filter(
        Tenant.status == TenantStatus.active
    ).count()

    vacant_units = total_units - occupied_units

    total_outstanding = db.query(func.sum(Tenant.balance)).filter(
        Tenant.status == TenantStatus.active,
        Tenant.balance > 0
    ).scalar() or 0.0

    total_collections = db.query(func.sum(Payment.amount)).filter(
        Payment.status == PaymentStatus.confirmed
    ).scalar() or 0.0

    return DashboardResponse(
        total_units=total_units,
        occupied_units=occupied_units,
        vacant_units=vacant_units,
        total_outstanding_debt=total_outstanding,
        total_collections=total_collections
    )