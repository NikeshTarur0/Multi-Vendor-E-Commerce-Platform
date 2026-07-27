from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.product import ProductOut, ProductCreate, ProductUpdate, CategoryOut
from app.services.product_service import ProductService
from app.models.product import Category
from app.dependencies.auth import get_current_vendor
from app.models.vendor import Vendor

router = APIRouter(prefix="/products", tags=["Products & Categories"])

@router.get("/categories", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return categories

@router.get("/", response_model=List[ProductOut])
def list_products(
    search: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    vendor_id: Optional[int] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    return ProductService.get_products(db, search, category_id, vendor_id, min_price, max_price)

@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return ProductService.get_product(db, product_id)

@router.post("/", response_model=ProductOut, status_code=201)
def create_product(
    req: ProductCreate,
    vendor: Vendor = Depends(get_current_vendor),
    db: Session = Depends(get_db)
):
    return ProductService.create_product(db, vendor.id, req)

@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: int,
    req: ProductUpdate,
    vendor: Vendor = Depends(get_current_vendor),
    db: Session = Depends(get_db)
):
    return ProductService.update_product(db, product_id, vendor.id, req)

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    vendor: Vendor = Depends(get_current_vendor),
    db: Session = Depends(get_db)
):
    ProductService.delete_product(db, product_id, vendor.id)
    return {"message": "Product removed successfully"}
