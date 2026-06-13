from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Tenant, Invoice, TenantStatus, InvoiceStatus
from app.services.sms_service import send_balance_reminder
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def run_billing_cycle():
    db: Session = SessionLocal()
    try:
        billing_period = datetime.now().strftime("%B %Y")
        active_tenants = db.query(Tenant).filter(
            Tenant.status == TenantStatus.active
        ).all()

        charged_count = 0
        for tenant in active_tenants:
            rent_amount = tenant.unit.rent_amount
            tenant.balance += rent_amount

            invoice = Invoice(
                tenant_id=tenant.id,
                amount=rent_amount,
                billing_period=billing_period,
                status=InvoiceStatus.unpaid
            )
            db.add(invoice)

            send_balance_reminder(
                tenant_id=tenant.id,
                phone=tenant.phone_number,
                name=tenant.name,
                balance=tenant.balance,
                unit=tenant.unit.unit_number,
                db=db
            )
            charged_count += 1

        db.commit()
        logger.info(f"Billing run complete — {charged_count} tenants charged for {billing_period}")
        return charged_count

    except Exception as e:
        db.rollback()
        logger.error(f"Billing run failed: {str(e)}")
        return 0
    finally:
        db.close()


def start_scheduler():
    # Runs on the 1st of every month at 8:00 AM
    scheduler.add_job(
        run_billing_cycle,
        CronTrigger(day=1, hour=8, minute=0),
        id="monthly_billing",
        replace_existing=True
    )
    scheduler.start()
    logger.info("Billing scheduler started — runs on 1st of every month at 08:00")


def stop_scheduler():
    scheduler.shutdown()