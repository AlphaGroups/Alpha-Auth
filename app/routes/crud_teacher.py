from sqlalchemy.orm import Session
from models import User, RoleEnum


from utils.security import hash_password


from app.schemas.teacher import TeacherCreate

def create_teacher(db: Session, teacher_data: TeacherCreate):
    # Check if email exists
    existing_user = db.query(User).filter(User.email == teacher_data.email).first()
    if existing_user:
        raise ValueError("Teacher with this email already exists")

    hashed_password = hash_password(teacher_data.password)

    teacher = User(
        name=teacher_data.full_name,
        email=teacher_data.email,
        mobile=teacher_data.mobile,
        hashed_password=hashed_password,
        role=RoleEnum.teacher,
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)

    return teacher
