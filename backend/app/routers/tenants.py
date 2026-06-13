from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Tenant, Unit, TenantStatus, UnitStatus
from app.schemas import TenantCreate, TenantUpdate, TenantResponse
from app.auth import get_current_admin

router = APIRouter()


@router.post("/", response_model=TenantResponse)
def create_tenant(
    payload: TenantCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    unit = db.query(Unit).filter(Unit.id == payload.unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    if unit.status != UnitStatus.active:
        raise HTTPException(status_code=400, detail="Unit is not available")
    existing_tenant = db.query(Tenant).filter(
        Tenant.unit_id == payload.unit_id,
        Tenant.status == TenantStatus.active
    ).first()
    if existing_tenant:
        raise HTTPException(status_code=400, detail="Unit is already occupied")

    tenant = Tenant(**payload.model_dump(), balance=unit.rent_amount)
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    from app.services.sms_service import send_onboarding_sms
    send_onboarding_sms(
        tenant_id=tenant.id,
        phone=tenant.phone_number,
        name=tenant.name,
        unit=unit.unit_number,
        lease_start=str(payload.lease_start_date),
        lease_end=str(payload.lease_end_date),
        db=db
    )
    return tenant

@router.get("/", response_model=List[TenantResponse])
def get_tenants(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    return db.query(Tenant).filter(Tenant.status == TenantStatus.active).all()


@router.get("/{tenant_id}", response_model=TenantResponse)
def get_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


@router.patch("/{tenant_id}", response_model=TenantResponse)
def update_tenant(
    tenant_id: int,
    payload: TenantUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(tenant, field, value)
    db.commit()
    db.refresh(tenant)
    return tenant


@router.post("/{tenant_id}/offboard")
def offboard_tenant(
    tenant_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    if tenant.status == TenantStatus.archived:
        raise HTTPException(status_code=400, detail="Tenant already offboarded")
    tenant.status = TenantStatus.archived
    db.commit()
    return {"message": f"{tenant.name} has been offboarded successfully"}