from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from app.schemas.teacher import TeacherCreate, TeacherResponse
from app.crud.crud_teacher import create_teacher
from auth.jwt import verify_token
from typing import List


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter()


@router.post("/teachers/", response_model=TeacherResponse)
def create_new_teacher(
    teacher_data: TeacherCreate, 
    college_id: int,
    created_by_admin_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Create a new teacher account
    """
    try:
        new_teacher = create_teacher(
            db, 
            teacher_data, 
            college_id, 
            created_by_admin_id
        )
        return new_teacher
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))