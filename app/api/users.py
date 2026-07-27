from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.user import UserOut, UserUpdate
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/profile", response_model=UserOut)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=UserOut)
def update_profile(req: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if req.full_name:
        current_user.full_name = req.full_name
    if req.email and req.email != current_user.email:
        existing = db.query(User).filter(User.email == req.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already taken")
        current_user.email = req.email
    db.commit()
    db.refresh(current_user)
    return current_user
