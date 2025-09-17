from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from app.schemas.teacher import TeacherCreate, TeacherOut
from models import RoleEnum, User, Admin
from .crud_teacher import create_teacher
from utils.security import require_role, get_current_user

router = APIRouter(prefix="/teachers", tags=["Teachers"])


@router.post(
    "/",
    response_model=TeacherOut,
    dependencies=[Depends(require_role([RoleEnum.admin.value, RoleEnum.superadmin.value]))],
)
def create_teacher_api(
    teacher_data: TeacherCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # get logged-in admin
):
    try:
        # If Admin, attach their college_id
        if current_user.role == RoleEnum.admin:
            admin = db.query(Admin).filter(Admin.user_id == current_user.id).first()
            if not admin:
                raise HTTPException(status_code=400, detail="Admin not found")
            college_id = admin.college_id
            created_by_admin_id = admin.id
        else:
            # SuperAdmin must explicitly provide a college_id (future option)
            college_id = teacher_data.college_id
            created_by_admin_id = None

        teacher = create_teacher(
            db,
            teacher_data,
            college_id=college_id,
            created_by_admin_id=created_by_admin_id,
        )
        return teacher
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
