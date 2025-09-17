from sqlalchemy.orm import Session
from models import Admin, College, User, RoleEnum

from utils.security import hash_password
from app.schemas.College_Admin import AdminCreate

def create_admin(db: Session, admin_data: AdminCreate):
    # Check if college exists
    college = db.query(College).filter(College.name == admin_data.college_name).first()
    if not college:
        college = College(name=admin_data.college_name)
        db.add(college)
        db.commit()
        db.refresh(college)

    # Check if email already used
    existing_admin = db.query(Admin).filter(Admin.email == admin_data.email).first()
    if existing_admin:
        raise ValueError("Admin with this email already exists")

    # Create admin entry
    new_admin = Admin(
        full_name=admin_data.full_name,
        email=admin_data.email,
        phone=admin_data.mobile,
        college_id=college.id,
    )
    db.add(new_admin)

    # Also create corresponding user with role=admin
    hashed_password = hash_password(admin_data.password)
    new_user = User(
        name=admin_data.full_name,
        email=admin_data.email,
        mobile=admin_data.mobile,
        hashed_password=hashed_password,
        role=RoleEnum.admin,
    )
    db.add(new_user)

    db.commit()
    db.refresh(new_admin)
    db.refresh(new_user)

    return new_admin
