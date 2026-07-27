from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="customer")  # 'customer', 'vendor', 'admin'
    is_verified = Column(Boolean, default=True)   # Enabled by default for easy demo testing
    verification_code = Column(String(64), nullable=True)
    reset_token = Column(String(64), nullable=True)
    status = Column(String(20), default="active") # 'active', 'suspended'
    phone = Column(String(20), nullable=True)
    address = Column(String(500), nullable=True)
    upi_vpa = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    vendor_profile = relationship("Vendor", back_populates="user", uselist=False)
    orders = relationship("Order", back_populates="customer")
    reviews = relationship("Review", back_populates="customer")
    wishlist_items = relationship("Wishlist", back_populates="customer")
