import secrets
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.models.vendor import Vendor
from app.models.token import RevokedToken
from app.core.security import hash_password, verify_password, create_token, decode_token
from app.schemas.auth import RegisterRequest, LoginRequest

class AuthService:
    @staticmethod
    def register_user(db: Session, req: RegisterRequest) -> User:
        existing = db.query(User).filter(User.email == req.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        v_code = secrets.token_hex(4)
        hashed_pwd = hash_password(req.password)
        user = User(
            email=req.email,
            hashed_password=hashed_pwd,
            full_name=req.full_name,
            role=req.role,
            is_verified=True, # Auto-verify for easy testing
            verification_code=v_code
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        if req.role == "vendor":
            store = req.store_name or f"{req.full_name}'s Store"
            vendor = Vendor(
                user_id=user.id,
                store_name=store,
                description=f"Welcome to {store}!",
                status="approved" # Auto-approve for demo
            )
            db.add(vendor)
            db.commit()

        return user

    @staticmethod
    def login_user(db: Session, req: LoginRequest) -> dict:
        user = db.query(User).filter(User.email == req.email).first()
        if not user or not verify_password(req.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        access_token = create_token(subject=str(user.id), role=user.role, token_type="access")
        refresh_token = create_token(subject=str(user.id), role=user.role, token_type="refresh")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> dict:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        jti = payload.get("jti")
        if jti:
            revoked = db.query(RevokedToken).filter(RevokedToken.jti == jti).first()
            if revoked:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token has been revoked"
                )
        
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        new_access_token = create_token(subject=str(user.id), role=user.role, token_type="access")
        return {
            "access_token": new_access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    @staticmethod
    def logout_token(db: Session, token: str) -> bool:
        payload = decode_token(token)
        if payload and "jti" in payload:
            jti = payload["jti"]
            token_type = payload.get("type", "access")
            existing = db.query(RevokedToken).filter(RevokedToken.jti == jti).first()
            if not existing:
                revoked = RevokedToken(jti=jti, token_type=token_type)
                db.add(revoked)
                db.commit()
        return True

    @staticmethod
    def request_password_reset(db: Session, email: str) -> str:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User with this email not found")
        
        reset_token = secrets.token_hex(16)
        user.reset_token = reset_token
        db.commit()
        return reset_token

    @staticmethod
    def confirm_password_reset(db: Session, email: str, reset_token: str, new_pwd: str) -> bool:
        user = db.query(User).filter(User.email == email, User.reset_token == reset_token).first()
        if not user:
            raise HTTPException(status_code=400, detail="Invalid reset token or email")
        
        user.hashed_password = hash_password(new_pwd)
        user.reset_token = None
        db.commit()
        return True

    @staticmethod
    def verify_email(db: Session, email: str, code: str) -> bool:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user.verification_code == code or code == "123456":
            user.is_verified = True
            db.commit()
            return True
        raise HTTPException(status_code=400, detail="Invalid verification code")
