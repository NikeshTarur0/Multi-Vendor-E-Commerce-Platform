from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_verified: bool
    status: str
    phone: Optional[str] = None
    address: Optional[str] = None
    upi_vpa: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    upi_vpa: Optional[str] = None
    new_password: Optional[str] = None
