from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def dashboard_placeholder():
    return {"message": "Dashboard router live"}