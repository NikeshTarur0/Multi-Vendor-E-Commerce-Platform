from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    is_verified: bool
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
