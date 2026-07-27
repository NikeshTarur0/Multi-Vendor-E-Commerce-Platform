from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class CartItemSchema(BaseModel):
    product_id: int
    quantity: int

class CheckoutRequest(BaseModel):
    items: List[CartItemSchema]
    shipping_address: str
    coupon_code: Optional[str] = None
    payment_method: str = "mock_card"

class OrderItemOut(BaseModel):
    id: int
    order_id: int
    product_id: int
    vendor_id: int
    price: float
    quantity: int
    item_status: str
    product_name: Optional[str] = None
    product_image: Optional[str] = None

    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    customer_id: int
    total_amount: float
    discount_amount: float
    final_amount: float
    coupon_code: Optional[str] = None
    payment_status: str
    order_status: str
    shipping_address: str
    created_at: datetime
    items: List[OrderItemOut] = []

    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    order_status: str
