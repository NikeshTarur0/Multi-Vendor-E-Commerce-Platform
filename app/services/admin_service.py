from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User
from app.models.vendor import Vendor
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.models.coupon import Coupon

class AdminService:
    @staticmethod
    def get_dashboard_stats(db: Session) -> dict:
        total_gmv = db.query(func.sum(Order.final_amount)).scalar() or 0.0
        total_orders = db.query(Order).count()
        total_vendors = db.query(Vendor).filter(Vendor.status == "approved").count()
        pending_vendors = db.query(Vendor).filter(Vendor.status == "pending").count()
        total_customers = db.query(User).filter(User.role == "customer").count()
        total_products = db.query(Product).filter(Product.status == "active").count()
        platform_commission = total_gmv * 0.10  # 10% platform fee simulation

        return {
            "total_gmv": round(total_gmv, 2),
            "platform_commission": round(platform_commission, 2),
            "total_orders": total_orders,
            "total_vendors": total_vendors,
            "pending_vendors": pending_vendors,
            "total_customers": total_customers,
            "total_products": total_products
        }

    @staticmethod
    def get_all_vendors(db: Session):
        vendors = db.query(Vendor).all()
        results = []
        for v in vendors:
            product_count = db.query(Product).filter(Product.vendor_id == v.id, Product.status == "active").count()
            results.append({
                "id": v.id,
                "store_name": v.store_name,
                "owner_email": v.user.email if v.user else "",
                "description": v.description,
                "rating": v.rating,
                "total_sales": round(v.total_sales, 2),
                "status": v.status,
                "product_count": product_count,
                "created_at": v.created_at
            })
        return results

    @staticmethod
    def update_vendor_status(db: Session, vendor_id: int, new_status: str) -> bool:
        vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
        if not vendor:
            return False
        vendor.status = new_status
        db.commit()
        return True
