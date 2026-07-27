from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_amount = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0.0)
    final_amount = Column(Float, nullable=False)
    coupon_code = Column(String(50), nullable=True)
    payment_status = Column(String(20), default="PENDING") # 'PENDING', 'PAID', 'FAILED'
    order_status = Column(String(20), default="PROCESSING") # 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED'
    shipping_address = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    customer = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("PaymentTransaction", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    item_status = Column(String(20), default="PROCESSING") # 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED'

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    transaction_ref = Column(String(100), unique=True, nullable=False)
    payment_method = Column(String(50), default="mock_card") # 'mock_card', 'mock_upi', 'mock_paypal'
    amount = Column(Float, nullable=False)
    status = Column(String(20), default="COMPLETED") # 'COMPLETED', 'FAILED', 'PENDING'
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    order = relationship("Order", back_populates="payments")
