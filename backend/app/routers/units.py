from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def units_placeholder():
    return {"message": "Units router live"}