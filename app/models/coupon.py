from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    discount_type = Column(String(20), default="percent") # 'percent', 'fixed'
    discount_value = Column(Float, nullable=False)
    min_order_amount = Column(Float, default=0.0)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True) # Null for global coupons
    max_uses = Column(Integer, default=100)
    current_uses = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    vendor = relationship("Vendor", back_populates="coupons")
