from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def payments_placeholder():
    return {"message": "Payments router live"}