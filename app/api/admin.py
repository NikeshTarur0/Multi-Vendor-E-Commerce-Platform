from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.admin_service import AdminService
from app.dependencies.auth import get_current_admin
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])

@router.get("/stats")
def get_stats(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return AdminService.get_dashboard_stats(db)

@router.get("/vendors")
def list_vendors(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)):
    return AdminService.get_all_vendors(db)

@router.put("/vendors/{vendor_id}/status")
def update_vendor_status(
    vendor_id: int,
    status: str,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    if status not in ["pending", "approved", "rejected", "suspended"]:
        raise HTTPException(status_code=400, detail="Invalid status value")
    
    success = AdminService.update_vendor_status(db, vendor_id, status)
    if not success:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return {"message": f"Vendor status updated to {status}"}
