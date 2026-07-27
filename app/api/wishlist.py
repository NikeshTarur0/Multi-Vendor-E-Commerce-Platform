from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.wishlist import WishlistCreate, WishlistOut
from app.models.wishlist import Wishlist
from app.models.product import Product
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.product_service import ProductService

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])

@router.get("/", response_model=List[WishlistOut])
def get_wishlist(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.query(Wishlist).filter(Wishlist.customer_id == current_user.id).order_by(Wishlist.id.desc()).all()
    results = []
    for item in items:
        w_out = WishlistOut.model_validate(item)
        if item.product:
            w_out.product = ProductService.get_product(db, item.product_id)
        results.append(w_out)
    return results

@router.post("/", response_model=WishlistOut, status_code=201)
def add_to_wishlist(
    req: WishlistCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == req.product_id, Product.status == "active").first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing = db.query(Wishlist).filter(
        Wishlist.customer_id == current_user.id,
        Wishlist.product_id == req.product_id
    ).first()
    if existing:
        w_out = WishlistOut.model_validate(existing)
        w_out.product = ProductService.get_product(db, existing.product_id)
        return w_out

    item = Wishlist(customer_id=current_user.id, product_id=req.product_id)
    db.add(item)
    db.commit()
    db.refresh(item)

    w_out = WishlistOut.model_validate(item)
    w_out.product = ProductService.get_product(db, item.product_id)
    return w_out

@router.delete("/{product_id}")
def remove_from_wishlist(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(Wishlist).filter(
        Wishlist.customer_id == current_user.id,
        Wishlist.product_id == product_id
    ).first()
    if item:
        db.delete(item)
        db.commit()
    return {"message": "Product removed from wishlist"}
