from sqlalchemy.orm import Session
from models import User, RoleEnum, Teacher
from utils.security import hash_password
from app.schemas.teacher import TeacherCreate

def create_teacher(db: Session, teacher_data: TeacherCreate, college_id: int, created_by_admin_id: int | None = None):
    # Check if email exists
    existing_user = db.query(User).filter(User.email == teacher_data.email).first()
    if existing_user:
        raise ValueError("Teacher with this email already exists")

    hashed_password = hash_password(teacher_data.password)

    teacher = Teacher(
        full_name=teacher_data.full_name,
        email=teacher_data.email,
        mobile=teacher_data.mobile,
        hashed_password=hashed_password,
        college_id=college_id,
        created_by_admin_id=created_by_admin_id,
    )

    db.add(teacher)
    db.commit()
    db.refresh(teacher)

    return teacher
