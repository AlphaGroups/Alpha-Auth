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

    # Check if user/email already exists
    existing_user = db.query(User).filter(User.email == admin_data.email).first()
    if existing_user:
        raise ValueError("Admin with this email already exists")

    # Create User first (so we can link to Admin)
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
    db.refresh(new_user)

    # Now create Admin and link user_id
    new_admin = Admin(
        user_id=new_user.id,      # ✅ link dynamic user id
        full_name=admin_data.full_name,
        email=admin_data.email,
        phone=admin_data.mobile,
        college_id=college.id,
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    return new_admin


def get_all_admins(db: Session):
    """
    Fetch all admins from the database with their related college.
    Returns a list of Admin objects.
    """
    return db.query(Admin).all()
