# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from database import get_db
# from app.schemas.teacher import TeacherCreate, TeacherOut
# from models import RoleEnum, User, Admin
# from .crud_teacher import create_teacher
# from utils.security import require_role, get_current_user

# router = APIRouter(prefix="/teachers", tags=["Teachers"])


# @router.post(
#     "/",
#     response_model=TeacherOut,
#     dependencies=[Depends(require_role([RoleEnum.admin.value, RoleEnum.superadmin.value]))],
# )
# def create_teacher_api(
#     teacher_data: TeacherCreate,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),  # logged-in user
# ):
#     """
#     Create a new Teacher.
#     - If role = Admin → teacher auto-linked to Admin's college
#     - If role = SuperAdmin → must provide `college_id`
#     """
#     try:
#         if current_user.role == RoleEnum.admin:
#             # Admin → bind teacher to their own college
#             admin = db.query(Admin).filter(Admin.user_id == current_user.id).first()
#             if not admin:
#                 raise HTTPException(status_code=400, detail="Admin not found")
#             college_id = admin.college_id
#             created_by_admin_id = admin.id
#         else:  # SuperAdmin
#             if not teacher_data.college_id:
#                 raise HTTPException(
#                     status_code=400,
#                     detail="SuperAdmin must provide a college_id",
#                 )
#             college_id = teacher_data.college_id
#             created_by_admin_id = None

#         teacher = create_teacher(
#             db,
#             teacher_data,
#             college_id=college_id,
#             created_by_admin_id=created_by_admin_id,
#         )
#         return teacher

#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from app.schemas.teacher import TeacherCreate, TeacherOut
from models import RoleEnum, User, Admin, Teacher
from .crud_teacher import create_teacher
from utils.security import require_role, get_current_user
from typing import List

router = APIRouter(prefix="/teachers", tags=["Teachers"])


# ✅ CREATE
@router.post(
    "/",
    response_model=TeacherOut,
    dependencies=[Depends(require_role([RoleEnum.admin.value, RoleEnum.superadmin.value]))],
)
def create_teacher_api(
    teacher_data: TeacherCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new Teacher.
    - Admin → auto-links to their own college
    - SuperAdmin → must provide `college_id`
    """
    if current_user.role == RoleEnum.admin:
        admin = db.query(Admin).filter(Admin.user_id == current_user.id).first()
        if not admin:
            raise HTTPException(status_code=400, detail="Admin not found")
        college_id = admin.college_id
        created_by_admin_id = admin.id
    else:  # SuperAdmin
        if not teacher_data.college_id:
            raise HTTPException(
                status_code=400,
                detail="SuperAdmin must provide a college_id",
            )
        college_id = teacher_data.college_id
        created_by_admin_id = None

    teacher = create_teacher(
        db,
        teacher_data,
        college_id=college_id,
        created_by_admin_id=created_by_admin_id,
    )
    return teacher


# ✅ READ - ALL
@router.get(
    "/",
    response_model=List[TeacherOut],
    dependencies=[Depends(require_role([RoleEnum.admin.value, RoleEnum.superadmin.value]))],
)
def get_teachers_api(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all Teachers.
    - Admin → only their college's teachers
    - SuperAdmin → all teachers
    """
    if current_user.role == RoleEnum.admin:
        admin = db.query(Admin).filter(Admin.user_id == current_user.id).first()
        if not admin:
            raise HTTPException(status_code=400, detail="Admin not found")
        teachers = db.query(Teacher).filter(Teacher.college_id == admin.college_id).all()
    else:
        teachers = db.query(Teacher).all()
    return teachers


# ✅ READ - ONE
@router.get(
    "/{teacher_id}",
    response_model=TeacherOut,
    dependencies=[Depends(require_role([RoleEnum.admin.value, RoleEnum.superadmin.value]))],
)
def get_teacher_api(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a single Teacher by ID.
    - Admin → must belong to their college
    - SuperAdmin → can access any teacher
    """
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    if current_user.role == RoleEnum.admin:
        admin = db.query(Admin).filter(Admin.user_id == current_user.id).first()
        if teacher.college_id != admin.college_id:
            raise HTTPException(status_code=403, detail="Not authorized")

    return teacher


# ✅ UPDATE
@router.put(
    "/{teacher_id}",
    response_model=TeacherOut,
    dependencies=[Depends(require_role([RoleEnum.admin.value, RoleEnum.superadmin.value]))],
)
def update_teacher_api(
    teacher_id: int,
    teacher_data: TeacherCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update Teacher details.
    - Admin → only teachers in their own college
    - SuperAdmin → can update any teacher
    """
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    if current_user.role == RoleEnum.admin:
        admin = db.query(Admin).filter(Admin.user_id == current_user.id).first()
        if teacher.college_id != admin.college_id:
            raise HTTPException(status_code=403, detail="Not authorized")

    teacher.full_name = teacher_data.full_name
    teacher.email = teacher_data.email
    teacher.mobile = teacher_data.mobile
    teacher.subject = teacher_data.subject
    db.commit()
    db.refresh(teacher)

    return teacher


# ✅ DELETE
@router.delete(
    "/{teacher_id}",
    response_model=dict,
    dependencies=[Depends(require_role([RoleEnum.admin.value, RoleEnum.superadmin.value]))],
)
def delete_teacher_api(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a Teacher.
    - Admin → only teachers in their own college
    - SuperAdmin → can delete any teacher
    """
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")

    if current_user.role == RoleEnum.admin:
        admin = db.query(Admin).filter(Admin.user_id == current_user.id).first()
        if teacher.college_id != admin.college_id:
            raise HTTPException(status_code=403, detail="Not authorized")

    db.delete(teacher)
    db.commit()
    return {"message": "Teacher deleted successfully"}
