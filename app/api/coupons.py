from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.coupon import CouponCreate, CouponOut, CouponValidateRequest
from app.services.coupon_service import CouponService
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/coupons", tags=["Coupons & Discounts"])

@router.post("/validate")
def validate_coupon(req: CouponValidateRequest, db: Session = Depends(get_db)):
    return CouponService.validate_coupon(db, req)

@router.get("/", response_model=List[CouponOut])
def list_coupons(db: Session = Depends(get_db)):
    return CouponService.get_coupons(db)

@router.post("/", response_model=CouponOut, status_code=201)
def create_coupon(
    req: CouponCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Admin or Vendor can create coupons
    if current_user.role not in ["admin", "vendor"]:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Only vendors or admins can create coupons")
    return CouponService.create_coupon(db, req)
