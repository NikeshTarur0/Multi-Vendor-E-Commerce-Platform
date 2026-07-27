from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.review import ReviewCreate, ReviewOut
from app.models.review import Review
from app.models.product import Product
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/reviews", tags=["Product Reviews"])

@router.get("/product/{product_id}", response_model=List[ReviewOut])
def get_product_reviews(product_id: int, db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(Review.product_id == product_id).order_by(Review.id.desc()).all()
    results = []
    for r in reviews:
        r_out = ReviewOut.model_validate(r)
        r_out.customer_name = r.customer.full_name if r.customer else "Anonymous Customer"
        results.append(r_out)
    return results

@router.post("/", response_model=ReviewOut, status_code=201)
def create_review(
    req: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == req.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    review = Review(
        product_id=req.product_id,
        customer_id=current_user.id,
        rating=req.rating,
        comment=req.comment
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    # Recalculate average rating
    all_reviews = db.query(Review).filter(Review.product_id == req.product_id).all()
    if all_reviews:
        product.rating_count = len(all_reviews)
        product.rating_avg = round(sum(r.rating for r in all_reviews) / float(len(all_reviews)), 1)
        db.commit()

    r_out = ReviewOut.model_validate(review)
    r_out.customer_name = current_user.full_name
    return r_out
