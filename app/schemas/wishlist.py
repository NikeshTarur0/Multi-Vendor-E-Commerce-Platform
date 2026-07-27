from pydantic import BaseModel
from datetime import datetime
from app.schemas.product import ProductOut

class WishlistCreate(BaseModel):
    product_id: int

class WishlistOut(BaseModel):
    id: int
    customer_id: int
    product_id: int
    created_at: datetime
    product: Optional[ProductOut] = None

    class Config:
        from_attributes = True
