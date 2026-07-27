from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.coupon import Coupon
from app.schemas.coupon import CouponCreate, CouponOut, CouponValidateRequest

class CouponService:
    @staticmethod
    def create_coupon(db: Session, req: CouponCreate) -> CouponOut:
        existing = db.query(Coupon).filter(Coupon.code == req.code.upper()).first()
        if existing:
            raise HTTPException(status_code=400, detail="Coupon code already exists")

        coupon = Coupon(
            code=req.code.upper(),
            discount_type=req.discount_type,
            discount_value=req.discount_value,
            min_order_amount=req.min_order_amount,
            max_uses=req.max_uses,
            vendor_id=req.vendor_id
        )
        db.add(coupon)
        db.commit()
        db.refresh(coupon)
        return CouponOut.model_validate(coupon)

    @staticmethod
    def validate_coupon(db: Session, req: CouponValidateRequest) -> dict:
        code = req.code.upper().strip()
        coupon = db.query(Coupon).filter(Coupon.code == code, Coupon.is_active == True).first()

        if not coupon:
            raise HTTPException(status_code=404, detail="Invalid or inactive coupon code")

        if coupon.current_uses >= coupon.max_uses:
            raise HTTPException(status_code=400, detail="Coupon usage limit reached")

        if req.cart_total < coupon.min_order_amount:
            raise HTTPException(
                status_code=400,
                detail=f"Cart total must be at least ${coupon.min_order_amount:.2f} for this coupon"
            )

        if coupon.vendor_id and req.vendor_ids:
            if coupon.vendor_id not in req.vendor_ids:
                raise HTTPException(status_code=400, detail="Coupon is not applicable for items in your cart")

        # Calculate discount
        if coupon.discount_type == "percent":
            discount = (req.cart_total * coupon.discount_value) / 100.0
        else: # fixed
            discount = coupon.discount_value

        discount = min(discount, req.cart_total)
        final_total = max(0.0, req.cart_total - discount)

        return {
            "valid": True,
            "code": coupon.code,
            "discount_type": coupon.discount_type,
            "discount_value": coupon.discount_value,
            "discount_amount": round(discount, 2),
            "final_amount": round(final_total, 2),
            "message": f"Coupon '{coupon.code}' applied successfully!"
        }

    @staticmethod
    def get_coupons(db: Session) -> List[CouponOut]:
        coupons = db.query(Coupon).all()
        return [CouponOut.model_validate(c) for c in coupons]
