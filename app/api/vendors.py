from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.vendor import VendorOut, VendorUpdate
from app.models.vendor import Vendor
from app.dependencies.auth import get_current_user, get_current_vendor
from app.models.user import User

router = APIRouter(prefix="/vendors", tags=["Vendors"])

@router.get("/", response_model=List[VendorOut])
def list_vendors(db: Session = Depends(get_db)):
    vendors = db.query(Vendor).filter(Vendor.status == "approved").all()
    return vendors

@router.get("/me", response_model=VendorOut)
def get_my_vendor_profile(vendor: Vendor = Depends(get_current_vendor)):
    return vendor

@router.get("/{vendor_id}", response_model=VendorOut)
def get_vendor(vendor_id: int, db: Session = Depends(get_db)):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor

@router.put("/me", response_model=VendorOut)
def update_my_vendor_profile(
    req: VendorUpdate,
    vendor: Vendor = Depends(get_current_vendor),
    db: Session = Depends(get_db)
):
    if req.store_name:
        vendor.store_name = req.store_name
    if req.description:
        vendor.description = req.description
    if req.logo_url:
        vendor.logo_url = req.logo_url
    db.commit()
    db.refresh(vendor)
    return vendor
