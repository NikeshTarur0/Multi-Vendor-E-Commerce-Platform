import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from app.core.config import settings

def hash_password(password: str) -> str:
    """Hash password using PBKDF2 with SHA256 and a random salt."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}${key.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against PBKDF2 hashed password."""
    try:
        salt, key_hex = hashed_password.split('$')
        key_check = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return secrets.compare_digest(key_check.hex(), key_hex)
    except Exception:
        return False

def create_token(subject: str, role: str, token_type: str = "access", expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT Token (access or refresh)."""
    now = datetime.utcnow()
    if expires_delta:
        expire = now + expires_delta
    else:
        if token_type == "access":
            expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        else:
            expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    payload: Dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "type": token_type,
        "iat": now,
        "exp": expire,
        "jti": secrets.token_hex(16)  # Unique token ID for tracking/blacklisting
    }
    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT Token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
