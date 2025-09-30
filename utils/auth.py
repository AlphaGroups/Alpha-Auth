# utils/auth.py
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Student
from utils.token import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_id = payload.get("sub")
    role = payload.get("role")
    
    try:
        uid = int(user_id)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # Fetch based on role
    if role in ["superadmin", "admin", "teacher"]:
        user = db.query(User).filter(User.id == uid).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
    elif role == "student":
        user = db.query(Student).filter(Student.id == uid).first()
        if not user:
            raise HTTPException(status_code=404, detail="Student not found")
    else:
        raise HTTPException(status_code=403, detail="Unknown role")

    user.current_role = role
    return user
