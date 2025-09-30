from sqlalchemy.orm import Session
from models import User, RoleEnum, Teacher
from utils.security import hash_password
from app.schemas.teacher import TeacherCreate


def create_teacher(
    db: Session,
    teacher_data: TeacherCreate,
    college_id: int,
    created_by_admin_id: int | None = None
):
    """
    Create a new Teacher user and record in teachers table.
    - Prevents duplicate emails across all users.
    - Automatically hashes password.
    - Binds teacher to the correct college.
    """
    # 🔍 Ensure email is not already used by any user
    existing_user = db.query(User).filter(User.email == teacher_data.email).first()
    if existing_user:
        raise ValueError("A user with this email already exists")

    # ✅ Create a User entry for teacher (with RoleEnum.teacher)
    hashed_password = hash_password(teacher_data.password)
    user = User(
        name=teacher_data.full_name,  # name field in User table
        first_name=teacher_data.full_name.split()[0],
        last_name=" ".join(teacher_data.full_name.split()[1:]) if len(teacher_data.full_name.split()) > 1 else None,
        email=teacher_data.email,
        mobile=teacher_data.mobile,
        hashed_password=hashed_password,
        role=RoleEnum.teacher,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # ✅ Create the Teacher entry linked to User
    teacher = Teacher(
        user_id=user.id,
        full_name=teacher_data.full_name,
        email=teacher_data.email,
        mobile=teacher_data.mobile,
        hashed_password=hashed_password,
        college_id=college_id,
        created_by_admin_id=created_by_admin_id,
        subject=teacher_data.subject,
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)

    return teacher
