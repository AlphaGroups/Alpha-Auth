from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from app.schemas.College_Admin import AdminCreate, AdminResponse
from app.crud.crud_admin import create_admin, get_all_admins
from auth.jwt import verify_token
from typing import List


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter()


@router.post("/admins/", response_model=AdminResponse)
def create_new_admin(admin_data: AdminCreate, db: Session = Depends(get_db)):
    """
    Create a new admin account
    """
    try:
        new_admin = create_admin(db, admin_data)
        return new_admin
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/admins/", response_model=List[AdminResponse])
def get_admins(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all admins
    """
    admins = get_all_admins(db)
    return admins