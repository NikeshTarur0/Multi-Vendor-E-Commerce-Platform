import secrets
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.product import Product
from app.models.vendor import Vendor
from app.models.coupon import Coupon
from app.models.order import Order, OrderItem, PaymentTransaction
from app.schemas.order import CheckoutRequest, OrderOut, OrderItemOut
from app.services.coupon_service import CouponService

class OrderService:
    @staticmethod
    def checkout_cart(db: Session, customer_id: int, req: CheckoutRequest) -> OrderOut:
        if not req.items:
            raise HTTPException(status_code=400, detail="Cart is empty")

        raw_total = 0.0
        order_items_data = []
        vendor_ids = set()

        # Validate products & stock
        for item in req.items:
            product = db.query(Product).filter(Product.id == item.product_id, Product.status == "active").first()
            if not product:
                raise HTTPException(status_code=400, detail=f"Product ID {item.product_id} not available")
            if product.stock < item.quantity:
                raise HTTPException(status_code=400, detail=f"Insufficient stock for '{product.name}' (Available: {product.stock})")

            item_total = product.price * item.quantity
            raw_total += item_total
            vendor_ids.add(product.vendor_id)

            order_items_data.append({
                "product": product,
                "vendor_id": product.vendor_id,
                "price": product.price,
                "quantity": item.quantity
            })

        # Apply coupon if provided
        discount_amount = 0.0
        if req.coupon_code:
            coupon = db.query(Coupon).filter(Coupon.code == req.coupon_code.upper(), Coupon.is_active == True).first()
            if coupon:
                if coupon.discount_type == "percent":
                    discount_amount = (raw_total * coupon.discount_value) / 100.0
                else:
                    discount_amount = coupon.discount_value
                discount_amount = min(discount_amount, raw_total)
                coupon.current_uses += 1

        final_amount = max(0.0, raw_total - discount_amount)

        # Create Order
        order = Order(
            customer_id=customer_id,
            total_amount=round(raw_total, 2),
            discount_amount=round(discount_amount, 2),
            final_amount=round(final_amount, 2),
            coupon_code=req.coupon_code.upper() if req.coupon_code else None,
            payment_status="PAID",
            order_status="PROCESSING",
            shipping_address=req.shipping_address
        )
        db.add(order)
        db.flush() # Get order.id

        # Create Order Items & Update Stock / Vendor sales
        for item_info in order_items_data:
            p = item_info["product"]
            order_item = OrderItem(
                order_id=order.id,
                product_id=p.id,
                vendor_id=p.vendor_id,
                price=item_info["price"],
                quantity=item_info["quantity"],
                item_status="PROCESSING"
            )
            db.add(order_item)

            # Reduce stock
            p.stock -= item_info["quantity"]

            # Update Vendor Total Sales
            vendor = db.query(Vendor).filter(Vendor.id == p.vendor_id).first()
            if vendor:
                vendor.total_sales += (item_info["price"] * item_info["quantity"])

        # Create Mock Payment Transaction
        tx_ref = f"TX-{secrets.token_hex(6).upper()}"
        payment_tx = PaymentTransaction(
            order_id=order.id,
            transaction_ref=tx_ref,
            payment_method=req.payment_method,
            amount=round(final_amount, 2),
            status="COMPLETED"
        )
        db.add(payment_tx)

        db.commit()
        db.refresh(order)

        return OrderService._format_order(db, order)

    @staticmethod
    def get_customer_orders(db: Session, customer_id: int) -> List[OrderOut]:
        orders = db.query(Order).filter(Order.customer_id == customer_id).order_by(Order.id.desc()).all()
        return [OrderService._format_order(db, o) for o in orders]

    @staticmethod
    def get_vendor_orders(db: Session, vendor_id: int) -> List[dict]:
        # Vendor sees line items belonging to their vendor_id
        items = db.query(OrderItem).filter(OrderItem.vendor_id == vendor_id).order_by(OrderItem.id.desc()).all()
        results = []
        for item in items:
            order = item.order
            results.append({
                "item_id": item.id,
                "order_id": order.id,
                "product_id": item.product_id,
                "product_name": item.product.name if item.product else "Product",
                "price": item.price,
                "quantity": item.quantity,
                "total": round(item.price * item.quantity, 2),
                "item_status": item.item_status,
                "shipping_address": order.shipping_address,
                "created_at": order.created_at
            })
        return results

    @staticmethod
    def update_vendor_item_status(db: Session, vendor_id: int, item_id: int, new_status: str) -> bool:
        item = db.query(OrderItem).filter(OrderItem.id == item_id, OrderItem.vendor_id == vendor_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Order line item not found")
        
        item.item_status = new_status
        db.commit()
        return True

    @staticmethod
    def get_all_orders(db: Session) -> List[OrderOut]:
        orders = db.query(Order).order_by(Order.id.desc()).all()
        return [OrderService._format_order(db, o) for o in orders]

    @staticmethod
    def _format_order(db: Session, order: Order) -> OrderOut:
        out = OrderOut.model_validate(order)
        out_items = []
        for item in order.items:
            item_out = OrderItemOut.model_validate(item)
            item_out.product_name = item.product.name if item.product else "Product"
            item_out.product_image = item.product.image_url if item.product else ""
            out_items.append(item_out)
        out.items = out_items
        return out
