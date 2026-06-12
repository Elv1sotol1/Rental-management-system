from sqlalchemy import (Column, Integer, String, Float,
                        DateTime, Date, Enum, Text,
                        ForeignKey, JSON)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


# --- ENUMS ---

class UnitStatus(str, enum.Enum):
    active = "Active"
    inactive = "Inactive"
    maintenance = "Under Maintenance"

class TenantStatus(str, enum.Enum):
    active = "Active"
    archived = "Archived"

class PaymentMethod(str, enum.Enum):
    mpesa = "M-Pesa STK Push"
    cash = "Manual Cash"

class PaymentStatus(str, enum.Enum):
    pending = "Pending"
    confirmed = "Confirmed"
    failed = "Failed"

class InvoiceStatus(str, enum.Enum):
    unpaid = "Unpaid"
    paid = "Paid"
    partial = "Partially Paid"

class SMSStatus(str, enum.Enum):
    sent = "Sent"
    delivered = "Delivered"
    failed = "Failed"


# --- TABLES ---

class Administrator(Base):
    __tablename__ = "administrators"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)


class Unit(Base):
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, index=True)
    unit_number = Column(String(20), unique=True, nullable=False)
    rent_amount = Column(Float, nullable=False)
    status = Column(Enum(UnitStatus), default=UnitStatus.active)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    tenants = relationship("Tenant", back_populates="unit")


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    phone_number = Column(String(20), nullable=False)
    balance = Column(Float, default=0.0)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False)
    lease_start_date = Column(Date, nullable=False)
    lease_end_date = Column(Date, nullable=False)
    status = Column(Enum(TenantStatus), default=TenantStatus.active)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    unit = relationship("Unit", back_populates="tenants")
    payments = relationship("Payment", back_populates="tenant")
    invoices = relationship("Invoice", back_populates="tenant")
    sms_logs = relationship("SMSLog", back_populates="tenant")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    mpesa_receipt_number = Column(String(20), unique=True, nullable=True)
    amount = Column(Float, nullable=False)
    phone_number = Column(String(20), nullable=True)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.pending)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    tenant = relationship("Tenant", back_populates="payments")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    amount = Column(Float, nullable=False)
    billing_period = Column(String(20), nullable=False)
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.unpaid)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    tenant = relationship("Tenant", back_populates="invoices")


class SMSLog(Base):
    __tablename__ = "sms_logs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    recipient_number = Column(String(20), nullable=False)
    message_body = Column(Text, nullable=False)
    delivery_status = Column(Enum(SMSStatus), default=SMSStatus.sent)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    tenant = relationship("Tenant", back_populates="sms_logs")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)
    target_entity = Column(String(100), nullable=True)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())