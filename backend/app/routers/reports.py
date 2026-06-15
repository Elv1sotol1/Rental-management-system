from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.auth import get_current_admin
from app.services.report_service import (
    generate_tenant_statement_pdf,
    generate_monthly_report_pdf,
    generate_portfolio_report_pdf,
    generate_tenant_statement_excel,
    generate_monthly_report_excel,
    generate_portfolio_report_excel,
)

router = APIRouter()


@router.get("/tenant/{tenant_id}/pdf")
def tenant_statement_pdf(
    tenant_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    buf = generate_tenant_statement_pdf(tenant_id, db)
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=tenant_{tenant_id}_statement.pdf"}
    )


@router.get("/tenant/{tenant_id}/excel")
def tenant_statement_excel(
    tenant_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    buf = generate_tenant_statement_excel(tenant_id, db)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=tenant_{tenant_id}_statement.xlsx"}
    )


@router.get("/monthly/pdf")
def monthly_report_pdf(
    month: str = Query(default=datetime.now().strftime("%Y-%m")),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    buf = generate_monthly_report_pdf(month, db)
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=collections_{month}.pdf"}
    )


@router.get("/monthly/excel")
def monthly_report_excel(
    month: str = Query(default=datetime.now().strftime("%Y-%m")),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    buf = generate_monthly_report_excel(month, db)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=collections_{month}.xlsx"}
    )


@router.get("/portfolio/pdf")
def portfolio_report_pdf(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    buf = generate_portfolio_report_pdf(db)
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=portfolio_report.pdf"}
    )


@router.get("/portfolio/excel")
def portfolio_report_excel(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    buf = generate_portfolio_report_excel(db)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=portfolio_report.xlsx"}
    )