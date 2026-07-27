from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.auth import (
    RegisterRequest, LoginRequest, RefreshTokenRequest,
    ForgotPasswordRequest, ResetPasswordRequest, VerifyEmailRequest, Token
)
from app.schemas.user import UserOut
from app.services.auth_service import AuthService
from app.dependencies.auth import get_current_user, security_scheme
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserOut, status_code=201)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    user = AuthService.register_user(db, req)
    return user

@router.post("/login", response_model=Token)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    return AuthService.login_user(db, req)

@router.post("/refresh", response_model=Token)
def refresh_token(req: RefreshTokenRequest, db: Session = Depends(get_db)):
    return AuthService.refresh_access_token(db, req.refresh_token)

@router.post("/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(security_scheme), db: Session = Depends(get_db)):
    if credentials:
        AuthService.logout_token(db, credentials.credentials)
    return {"message": "Successfully logged out"}

@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    token = AuthService.request_password_reset(db, req.email)
    return {"message": "Password reset token generated", "reset_token": token}

@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    AuthService.confirm_password_reset(db, req.email, req.reset_token, req.new_password)
    return {"message": "Password updated successfully"}

@router.post("/verify-email")
def verify_email(req: VerifyEmailRequest, db: Session = Depends(get_db)):
    AuthService.verify_email(db, req.email, req.verification_code)
    return {"message": "Email verified successfully"}

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
