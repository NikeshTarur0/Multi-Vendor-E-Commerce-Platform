from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.product import Product, Category
from app.models.vendor import Vendor
from app.schemas.product import ProductCreate, ProductUpdate, ProductOut

class ProductService:
    @staticmethod
    def get_products(
        db: Session,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        vendor_id: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> List[ProductOut]:
        query = db.query(Product).filter(Product.status == "active")

        if search:
            query = query.filter(Product.name.ilike(f"%{search}%") | Product.description.ilike(f"%{search}%"))
        if category_id:
            query = query.filter(Product.category_id == category_id)
        if vendor_id:
            query = query.filter(Product.vendor_id == vendor_id)
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        if max_price is not None:
            query = query.filter(Product.price <= max_price)

        products = query.order_by(Product.id.desc()).all()
        result = []
        for p in products:
            p_out = ProductOut.model_validate(p)
            p_out.vendor_store_name = p.vendor.store_name if p.vendor else "Unknown Vendor"
            p_out.category_name = p.category.name if p.category else "General"
            result.append(p_out)

        return result

    @staticmethod
    def get_product(db: Session, product_id: int) -> ProductOut:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        p_out = ProductOut.model_validate(product)
        p_out.vendor_store_name = product.vendor.store_name if product.vendor else "Unknown Vendor"
        p_out.category_name = product.category.name if product.category else "General"
        return p_out

    @staticmethod
    def create_product(db: Session, vendor_id: int, req: ProductCreate) -> ProductOut:
        category = db.query(Category).filter(Category.id == req.category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="Invalid Category ID")

        product = Product(
            vendor_id=vendor_id,
            category_id=req.category_id,
            name=req.name,
            description=req.description,
            price=req.price,
            stock=req.stock,
            image_url=req.image_url or "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500"
        )
        db.add(product)
        db.commit()
        db.refresh(product)

        p_out = ProductOut.model_validate(product)
        p_out.vendor_store_name = product.vendor.store_name if product.vendor else ""
        p_out.category_name = category.name
        return p_out

    @staticmethod
    def update_product(db: Session, product_id: int, vendor_id: int, req: ProductUpdate) -> ProductOut:
        product = db.query(Product).filter(Product.id == product_id, Product.vendor_id == vendor_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found or unauthorized")

        for field, value in req.model_dump(exclude_unset=True).items():
            setattr(product, field, value)

        db.commit()
        db.refresh(product)
        p_out = ProductOut.model_validate(product)
        p_out.vendor_store_name = product.vendor.store_name if product.vendor else ""
        p_out.category_name = product.category.name if product.category else ""
        return p_out

    @staticmethod
    def delete_product(db: Session, product_id: int, vendor_id: int) -> bool:
        product = db.query(Product).filter(Product.id == product_id, Product.vendor_id == vendor_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found or unauthorized")
        
        product.status = "inactive"
        db.commit()
        return True
