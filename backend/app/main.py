from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, units, tenants, payments, mpesa, billing, dashboard, reports

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Rental Management System API",
    description="Property & Lease Management Platform",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(units.router, prefix="/api/v1/units", tags=["Units"])
app.include_router(tenants.router, prefix="/api/v1/tenants", tags=["Tenants"])
app.include_router(payments.router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(mpesa.router, prefix="/api/v1/mpesa", tags=["M-Pesa"])
app.include_router(billing.router, prefix="/api/v1/billing", tags=["Billing"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])

@app.get("/")
def root():
    return {"message": "RMS API v2.0 is running"}