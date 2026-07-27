from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.order import CheckoutRequest, OrderOut, OrderStatusUpdate
from app.services.order_service import OrderService
from app.dependencies.auth import get_current_user, get_current_vendor, get_current_admin
from app.models.user import User
from app.models.vendor import Vendor

router = APIRouter(prefix="/orders", tags=["Orders & Checkout"])

@router.post("/checkout", response_model=OrderOut, status_code=201)
def checkout(
    req: CheckoutRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return OrderService.checkout_cart(db, current_user.id, req)

@router.get("/my-orders", response_model=List[OrderOut])
def get_my_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return OrderService.get_customer_orders(db, current_user.id)

@router.get("/vendor-orders")
def get_vendor_orders(
    vendor: Vendor = Depends(get_current_vendor),
    db: Session = Depends(get_db)
):
    return OrderService.get_vendor_orders(db, vendor.id)

@router.put("/vendor-order-items/{item_id}/status")
def update_vendor_item_status(
    item_id: int,
    req: OrderStatusUpdate,
    vendor: Vendor = Depends(get_current_vendor),
    db: Session = Depends(get_db)
):
    OrderService.update_vendor_item_status(db, vendor.id, item_id, req.order_status)
    return {"message": f"Order line item status updated to {req.order_status}"}

@router.get("/all", response_model=List[OrderOut])
def get_all_orders_admin(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return OrderService.get_all_orders(db)
