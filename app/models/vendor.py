from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    store_name = Column(String(255), unique=True, nullable=False)
    description = Column(String(1000), nullable=True)
    logo_url = Column(String(500), nullable=True)
    rating = Column(Float, default=5.0)
    total_sales = Column(Float, default=0.0)
    status = Column(String(20), default="approved") # 'pending', 'approved', 'rejected'
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="vendor_profile")
    products = relationship("Product", back_populates="vendor")
    coupons = relationship("Coupon", back_populates="vendor")
