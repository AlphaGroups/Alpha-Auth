from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from app.schemas.student import StudentCreate, StudentResponse
from app.crud.crud_temp_user import create_temp_user
from auth.jwt import verify_token
from typing import List


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter()


@router.post("/students/", response_model=StudentResponse)
def create_new_student(student_data: StudentCreate, db: Session = Depends(get_db)):
    """
    Create a new student account (registers to temp_users initially for email verification)
    """
    try:
        # Create student in temp_users table initially
        temp_user = create_temp_user(
            db, 
            name=student_data.full_name, 
            email=student_data.email, 
            password=student_data.password
        )
        
        # For now, return a basic response since we don't have a specific CRUD for students yet
        # In a full implementation, we'd need a student CRUD module
        return StudentResponse(
            id=temp_user.id,
            full_name=temp_user.name,
            email=temp_user.email,
            mobile=student_data.mobile,
            college_id=1,  # Placeholder - would need to be passed in
            roll_number=student_data.roll_number,
            course=student_data.course
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))