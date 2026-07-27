from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class VendorCreate(BaseModel):
    store_name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None

class VendorUpdate(BaseModel):
    store_name: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    status: Optional[str] = None

class VendorOut(BaseModel):
    id: int
    user_id: int
    store_name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    rating: float
    total_sales: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
