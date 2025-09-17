from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from app.schemas.teacher import TeacherCreate, TeacherOut
from models import RoleEnum
from .crud_teacher import create_teacher
from utils.security import require_role

router = APIRouter(prefix="/teachers", tags=["Teachers"])

@router.post(
    "/", 
    response_model=TeacherOut,
    dependencies=[Depends(require_role([RoleEnum.admin.value, RoleEnum.superadmin.value]))]
)
def create_teacher_api(teacher_data: TeacherCreate, db: Session = Depends(get_db)):
    try:
        teacher = create_teacher(db, teacher_data)
        return teacher
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
