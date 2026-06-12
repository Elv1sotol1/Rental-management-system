from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def tenants_placeholder():
    return {"message": "Tenants router live"}