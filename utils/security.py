from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from auth.jwt import verify_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ OAuth2 scheme - should match the tokenUrl in your router
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# ---------- Password Helpers ----------
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# ---------- DB Dependency ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- Current User ----------
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify the token
        payload = verify_token(token)
        if payload is None:
            raise credentials_exception
            
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
    except Exception:
        raise credentials_exception

    # Get user from database
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    
    return user

# ---------- Role Hierarchy ----------
role_hierarchy = {
    "superadmin": ["admin", "teacher", "student"],
    "admin": ["teacher", "student"], 
    "teacher": ["student"],
    "student": []
}

def can_create_role(requester_role: str, target_role: str):
    """Check if requester can create target role"""
    return target_role in role_hierarchy.get(requester_role, [])

# ---------- Role-based Dependencies ----------
def require_role(required_roles: list[str]):
    """Dependency factory for role-based access control"""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role.value not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {required_roles}"
            )
        return current_user
    return role_checker

# Convenience dependencies for common role checks
require_superadmin = require_role(["superadmin"])
require_admin_or_above = require_role(["superadmin", "admin"])
require_teacher_or_above = require_role(["superadmin", "admin", "teacher"])