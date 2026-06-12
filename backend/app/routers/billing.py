from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def billing_placeholder():
    return {"message": "Billing router live"}