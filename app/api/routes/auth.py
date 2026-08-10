from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/auth", tags=["Auth"])


# ── REQUEST SCHEMAS ───────────────────────────────────────
class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    phone: Optional[str] = None
    upi_id: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


# ── REGISTER ──────────────────────────────────────────────
@router.post("/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    
    # Check if email already exists
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    new_user = User(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        upi_id=payload.upi_id,
        hashed_password=hash_password(payload.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate token
    token = create_access_token(new_user.id)

    return {
        "message": "Registration successful",
        "access_token": token,
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email
        }
    }


# ── LOGIN ─────────────────────────────────────────────────
@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):

    # Find user by email
    user = db.query(User).filter(User.email == payload.email).first()
    
    # Check if user exists and password is correct
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Generate token
    token = create_access_token(user.id)

    return {
        "message": "Login successful",
        "access_token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }