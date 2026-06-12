from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def reports_placeholder():
    return {"message": "Reports router live"}