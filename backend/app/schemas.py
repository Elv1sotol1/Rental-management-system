from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from app.models import UnitStatus, TenantStatus, PaymentMethod, PaymentStatus, InvoiceStatus


# --- AUTH ---

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- UNITS ---

class UnitCreate(BaseModel):
    unit_number: str
    rent_amount: float

class UnitUpdate(BaseModel):
    unit_number: Optional[str] = None
    rent_amount: Optional[float] = None
    status: Optional[UnitStatus] = None

class UnitResponse(BaseModel):
    id: int
    unit_number: str
    rent_amount: float
    status: UnitStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_occupied: bool = False

    class Config:
        from_attributes = True


# --- TENANTS ---

class TenantCreate(BaseModel):
    name: str
    phone_number: str
    unit_id: int
    lease_start_date: date
    lease_end_date: date

class TenantUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    lease_start_date: Optional[date] = None
    lease_end_date: Optional[date] = None

class TenantResponse(BaseModel):
    id: int
    name: str
    phone_number: str
    balance: float
    unit_id: int
    lease_start_date: date
    lease_end_date: date
    status: TenantStatus
    created_at: datetime

    class Config:
        from_attributes = True


# --- PAYMENTS ---

class ManualPaymentCreate(BaseModel):
    tenant_id: int
    amount: float

class PaymentResponse(BaseModel):
    id: int
    tenant_id: int
    amount: float
    phone_number: Optional[str] = None
    payment_method: PaymentMethod
    status: PaymentStatus
    mpesa_receipt_number: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


# --- DASHBOARD ---

class DashboardResponse(BaseModel):
    total_units: int
    occupied_units: int
    vacant_units: int
    total_outstanding_debt: float
    total_collections: float