from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def mpesa_placeholder():
    return {"message": "M-Pesa router live"}