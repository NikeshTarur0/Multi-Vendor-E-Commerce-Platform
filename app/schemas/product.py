from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CategoryOut(BaseModel):
    id: int
    name: str
    slug: str
    icon: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    category_id: int
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 10
    image_url: Optional[str] = None

class ProductUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    image_url: Optional[str] = None
    status: Optional[str] = None

class ProductOut(BaseModel):
    id: int
    vendor_id: int
    category_id: int
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    image_url: Optional[str] = None
    status: str
    rating_avg: float
    rating_count: int
    created_at: datetime
    vendor_store_name: Optional[str] = None
    category_name: Optional[str] = None

    class Config:
        from_attributes = True
