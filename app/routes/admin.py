from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from app.schemas.College_Admin import AdminCreate, AdminResponse
from app.routes.crud_admin import create_admin
from utils.security import require_superadmin  # 👈 add this

router = APIRouter(prefix="/admins", tags=["Admins"])

@router.post("/", response_model=AdminResponse, dependencies=[Depends(require_superadmin)])
def create_admin_api(admin_data: AdminCreate, db: Session = Depends(get_db)):
    try:
        admin = create_admin(db, admin_data)
        return AdminResponse(
            id=admin.id,
            
            full_name=admin.full_name,
            email=admin.email,
            mobile=admin.phone,
            college=admin.college.name,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError as e:
        db.rollback()
        if "users.email" in str(e.orig):
            raise HTTPException(status_code=400, detail="Email already exists")
        raise HTTPException(status_code=400, detail="Database integrity error")
