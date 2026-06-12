import requests
import base64
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET")
SHORTCODE = os.getenv("MPESA_SHORTCODE")
PASSKEY = os.getenv("MPESA_PASSKEY")
CALLBACK_URL = os.getenv("MPESA_CALLBACK_URL")
ENVIRONMENT = os.getenv("MPESA_ENVIRONMENT", "sandbox")

if ENVIRONMENT == "sandbox":
    BASE_URL = "https://sandbox.safaricom.co.ke"
else:
    BASE_URL = "https://api.safaricom.co.ke"


def get_access_token() -> str:
    url = f"{BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=(CONSUMER_KEY, CONSUMER_SECRET))
    response.raise_for_status()
    return response.json()["access_token"]


def generate_password() -> tuple[str, str]:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    raw = f"{SHORTCODE}{PASSKEY}{timestamp}"
    password = base64.b64encode(raw.encode()).decode()
    return password, timestamp


def stk_push(phone_number: str, amount: int, account_ref: str = "RentPayment") -> dict:
    access_token = get_access_token()
    password, timestamp = generate_password()

    # Normalize phone number to 2547XXXXXXXX format
    phone = phone_number.strip()
    if phone.startswith("+"):
        phone = phone[1:]
    elif phone.startswith("0"):
        phone = "254" + phone[1:]

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": account_ref,
        "TransactionDesc": "Rent Payment"
    }

    response = requests.post(
        f"{BASE_URL}/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers=headers
    )
    return response.json()