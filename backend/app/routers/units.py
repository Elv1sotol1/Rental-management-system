from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Unit, Tenant, TenantStatus, UnitStatus
from app.schemas import UnitCreate, UnitUpdate, UnitResponse
from app.auth import get_current_admin

router = APIRouter()


@router.post("/", response_model=UnitResponse)
def create_unit(
    payload: UnitCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    existing = db.query(Unit).filter(Unit.unit_number == payload.unit_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Unit number already exists")
    unit = Unit(**payload.model_dump())
    db.add(unit)
    db.commit()
    db.refresh(unit)
    active_tenant = db.query(Tenant).filter(
        Tenant.unit_id == unit.id,
        Tenant.status == TenantStatus.active
    ).first()
    unit_data = UnitResponse.model_validate(unit)
    unit_data.is_occupied = active_tenant is not None
    return unit_data


@router.get("/", response_model=List[UnitResponse])
def get_units(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    units = db.query(Unit).filter(Unit.status != UnitStatus.inactive).all()
    result = []
    for unit in units:
        active_tenant = db.query(Tenant).filter(
            Tenant.unit_id == unit.id,
            Tenant.status == TenantStatus.active
        ).first()
        unit_data = UnitResponse.model_validate(unit)
        unit_data.is_occupied = active_tenant is not None
        result.append(unit_data)
    return result


@router.get("/{unit_id}", response_model=UnitResponse)
def get_unit(
    unit_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    active_tenant = db.query(Tenant).filter(
        Tenant.unit_id == unit.id,
        Tenant.status == TenantStatus.active
    ).first()
    unit_data = UnitResponse.model_validate(unit)
    unit_data.is_occupied = active_tenant is not None
    return unit_data


@router.patch("/{unit_id}", response_model=UnitResponse)
def update_unit(
    unit_id: int,
    payload: UnitUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(unit, field, value)
    db.commit()
    db.refresh(unit)
    unit_data = UnitResponse.model_validate(unit)
    return unit_data


@router.delete("/{unit_id}")
def delete_unit(
    unit_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    active_tenant = db.query(Tenant).filter(
        Tenant.unit_id == unit_id,
        Tenant.status == TenantStatus.active
    ).first()
    if active_tenant:
        raise HTTPException(status_code=400, detail="Cannot delete unit with active tenant")
    unit.status = UnitStatus.inactive
    db.commit()
    return {"message": f"Unit {unit.unit_number} deactivated successfully"}