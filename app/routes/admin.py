# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import IntegrityError
# from database import get_db
# from app.schemas.College_Admin import AdminCreate, AdminResponse

# from app.routes.crud_admin import create_admin, get_all_admins
# from utils.security import require_superadmin  # 👈 add this

# router = APIRouter(prefix="/admins", tags=["Admins"])

# @router.post("/", response_model=AdminResponse, dependencies=[Depends(require_superadmin)])
# def create_admin_api(admin_data: AdminCreate, db: Session = Depends(get_db)):
#     try:
#         admin = create_admin(db, admin_data)
#         return AdminResponse(
#             id=admin.id,
            
#             full_name=admin.full_name,
#             email=admin.email,
#             mobile=admin.phone,
#             college_name=admin.college.name,
#         )
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     except IntegrityError as e:
#         db.rollback()
#         if "users.email" in str(e.orig):
#             raise HTTPException(status_code=400, detail="Email already exists")
#         raise HTTPException(status_code=400, detail="Database integrity error")


# @router.get("/", response_model=list[AdminResponse], dependencies=[Depends(require_superadmin)])
# def get_admins(db: Session = Depends(get_db)):

#     admins = get_all_admins(db)  # Implement in crud_admin.py
#     return [
#         AdminResponse(
#             id=admin.id,
#             full_name=admin.full_name,
#             email=admin.email,
#             mobile=admin.phone,
#             college_name=admin.college.name,
#         )
#         for admin in admins
#     ]

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from app.schemas.College_Admin import AdminCreate, AdminResponse
from app.routes.crud_admin import create_admin, get_all_admins
from models import Admin
from utils.security import require_superadmin

router = APIRouter(prefix="/admins", tags=["Admins"])


# ✅ CREATE
@router.post("/", response_model=AdminResponse, dependencies=[Depends(require_superadmin)])
def create_admin_api(admin_data: AdminCreate, db: Session = Depends(get_db)):
    try:
        admin = create_admin(db, admin_data)
        return AdminResponse(
            id=admin.id,
            full_name=admin.full_name,
            email=admin.email,
            mobile=admin.phone,
            college_name=admin.college.name,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError as e:
        db.rollback()
        if "users.email" in str(e.orig):
            raise HTTPException(status_code=400, detail="Email already exists")
        raise HTTPException(status_code=400, detail="Database integrity error")


# ✅ READ - ALL
@router.get("/", response_model=list[AdminResponse], dependencies=[Depends(require_superadmin)])
def get_admins(db: Session = Depends(get_db)):
    admins = get_all_admins(db)
    return [
        AdminResponse(
            id=admin.id,
            full_name=admin.full_name,
            email=admin.email,
            mobile=admin.phone,
            college_name=admin.college.name,
        )
        for admin in admins
    ]


# ✅ READ - ONE
@router.get("/{admin_id}", response_model=AdminResponse, dependencies=[Depends(require_superadmin)])
def get_admin(admin_id: int, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return AdminResponse(
        id=admin.id,
        full_name=admin.full_name,
        email=admin.email,
        mobile=admin.phone,
        college_name=admin.college.name,
    )


# ✅ UPDATE
@router.put("/{admin_id}", response_model=AdminResponse, dependencies=[Depends(require_superadmin)])
def update_admin(admin_id: int, admin_data: AdminCreate, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    admin.full_name = admin_data.full_name
    admin.email = admin_data.email
    admin.phone = admin_data.mobile

    db.commit()
    db.refresh(admin)

    return AdminResponse(
        id=admin.id,
        full_name=admin.full_name,
        email=admin.email,
        mobile=admin.phone,
        college_name=admin.college.name,
    )


# ✅ DELETE
@router.delete("/{admin_id}", response_model=dict, dependencies=[Depends(require_superadmin)])
def delete_admin(admin_id: int, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    db.delete(admin)
    db.commit()
    return {"message": "Admin deleted successfully"}
