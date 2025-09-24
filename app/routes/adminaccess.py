from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from utils.auth import get_current_user
from database import get_db
from models import AdminClassAccess
from utils.adminVideos import grant_admin_class_access

router = APIRouter(prefix="/adminaccess", tags=["AdminAccess"])

def grant_admin_class_access(db: Session, admin_id: int, class_ids: list[int]):
    for class_id in class_ids:
        # Check if access already exists
        existing = db.query(AdminClassAccess).filter_by(admin_id=admin_id, class_id=class_id).first()
        if not existing:
            access = AdminClassAccess(admin_id=admin_id, class_id=class_id)
            db.add(access)
    db.commit()

@router.post("/grant")
def grant_access(admin_id: int, class_ids: list[int], db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Only superadmin can grant access")

    grant_admin_class_access(db, admin_id, class_ids)
    return {"message": f"Admin {admin_id} now has access to classes {class_ids}"}
