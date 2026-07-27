from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CouponCreate(BaseModel):
    code: str
    discount_type: str = "percent" # 'percent' or 'fixed'
    discount_value: float
    min_order_amount: float = 0.0
    max_uses: int = 100
    vendor_id: Optional[int] = None # Optional for vendor specific, None for global

class CouponValidateRequest(BaseModel):
    code: str
    cart_total: float
    vendor_ids: Optional[list[int]] = []

class CouponOut(BaseModel):
    id: int
    code: str
    discount_type: str
    discount_value: float
    min_order_amount: float
    vendor_id: Optional[int] = None
    max_uses: int
    current_uses: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
