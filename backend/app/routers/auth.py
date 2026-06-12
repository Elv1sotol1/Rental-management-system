from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models import Administrator
from app.schemas import LoginRequest, TokenResponse
from app.auth import hash_password, verify_password, create_access_token

router = APIRouter()


@router.post("/setup")
def setup_admin(db: Session = Depends(get_db)):
    existing = db.query(Administrator).first()
    if existing:
        raise HTTPException(status_code=400, detail="Admin already exists")
    admin = Administrator(
        username="admin",
        hashed_password=hash_password("admin1234")
    )
    db.add(admin)
    db.commit()
    return {"message": "Admin created. Username: admin | Password: admin1234"}


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    admin = db.query(Administrator).filter(
        Administrator.username == payload.username
    ).first()
    if not admin or not verify_password(payload.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    admin.last_login = datetime.utcnow()
    db.commit()
    token = create_access_token({"sub": admin.username})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/logout")
def logout():
    return {"message": "Logged out successfully"}