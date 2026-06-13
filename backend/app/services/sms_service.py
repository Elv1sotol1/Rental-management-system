import africastalking
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.models import SMSLog, SMSStatus
import os
import logging

load_dotenv()

logger = logging.getLogger(__name__)

AT_USERNAME = os.getenv("AT_USERNAME")
AT_API_KEY = os.getenv("AT_API_KEY")
AT_SENDER_ID = os.getenv("AT_SENDER_ID", "RMS")

africastalking.initialize(AT_USERNAME, AT_API_KEY)
sms = africastalking.SMS


def send_sms(tenant_id: int, phone_number: str, message: str, db: Session) -> bool:
    log = SMSLog(
        tenant_id=tenant_id,
        recipient_number=phone_number,
        message_body=message,
        delivery_status=SMSStatus.sent
    )
    try:
        response = sms.send(message, [phone_number], AT_SENDER_ID)
        recipients = response.get("SMSMessageData", {}).get("Recipients", [])
        if recipients and recipients[0].get("status") == "Success":
            log.delivery_status = SMSStatus.delivered
            logger.info(f"SMS delivered to {phone_number}")
        else:
            log.delivery_status = SMSStatus.failed
            logger.warning(f"SMS failed to {phone_number}: {response}")
        db.add(log)
        db.commit()
        return log.delivery_status == SMSStatus.delivered
    except Exception as e:
        log.delivery_status = SMSStatus.failed
        db.add(log)
        db.commit()
        logger.error(f"SMS exception for {phone_number}: {str(e)}")
        return False


def send_payment_confirmation(tenant_id: int, phone: str, name: str, amount: float, balance: float, receipt: str, db: Session):
    message = (
        f"Dear {name}, payment of KES {amount:.0f} received. "
        f"Receipt: {receipt}. "
        f"Outstanding balance: KES {balance:.0f}. "
        f"Thank you."
    )
    send_sms(tenant_id, phone, message, db)


def send_balance_reminder(tenant_id: int, phone: str, name: str, balance: float, unit: str, db: Session):
    message = (
        f"Dear {name}, your rent balance for Unit {unit} "
        f"is KES {balance:.0f}. "
        f"Please make payment to avoid penalties. Thank you."
    )
    send_sms(tenant_id, phone, message, db)


def send_onboarding_sms(tenant_id: int, phone: str, name: str, unit: str, lease_start: str, lease_end: str, db: Session):
    message = (
        f"Welcome {name}! You have been registered as a tenant "
        f"in Unit {unit}. Lease: {lease_start} to {lease_end}. "
        f"Contact management for any queries."
    )
    send_sms(tenant_id, phone, message, db)