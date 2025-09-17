from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models
from app.schemas.College_Admin import CollegeCreate, CollegeOut
from utils.security import hash_password, require_role
from models import RoleEnum

router = APIRouter(prefix="/colleges", tags=["Colleges"])

@router.post(
    "/", 
    response_model=CollegeOut,
    dependencies=[Depends(require_role([RoleEnum.superadmin.value]))]  # ✅ Only superadmin
)
def create_college(college: CollegeCreate, db: Session = Depends(get_db)):
    # Check if college exists
    existing = db.query(models.College).filter(models.College.name == college.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="College already exists")

    # Create new college
    new_college = models.College(name=college.name)
    db.add(new_college)
    db.commit()
    db.refresh(new_college)

    # Check if admin email already exists
    existing_admin = db.query(models.User).filter(models.User.email == college.admin_email).first()
    if existing_admin:
        raise HTTPException(status_code=400, detail="Admin with this email already exists")

    # Create admin in users
    admin_user = models.User(
        name=college.admin_full_name,
        email=college.admin_email,
        mobile=college.admin_mobile,
        hashed_password=hash_password(college.admin_password),
        role=RoleEnum.admin,
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)

    # Create admin record linked to college
    admin_record = models.Admin(
        full_name=college.admin_full_name,
        email=college.admin_email,
        phone=college.admin_mobile,
        college_id=new_college.id
    )
    db.add(admin_record)
    db.commit()

    return new_college
