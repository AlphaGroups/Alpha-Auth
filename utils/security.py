# from passlib.context import CryptContext
# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from sqlalchemy.orm import Session
# from database import SessionLocal
# from models import User
# from auth.jwt import verify_token
# # At the top of utils/security.py
# from database import get_db, SessionLocal  # make sure you have SessionLocal defined
# from models import Student, User, RoleEnum


# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# # ✅ OAuth2 scheme - should match the tokenUrl in your router
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# # ---------- Password Helpers ----------
# def hash_password(password: str):
#     return pwd_context.hash(password)

# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)

# # ---------- DB Dependency ----------
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # ---------- Current User ----------
# # def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
# #     """Get current user from JWT token"""
# #     credentials_exception = HTTPException(
# #         status_code=status.HTTP_401_UNAUTHORIZED,
# #         detail="Could not validate credentials",
# #         headers={"WWW-Authenticate": "Bearer"},
# #     )
    
# #     try:
# #         # Verify the token
# #         payload = verify_token(token)
# #         if payload is None:
# #             raise credentials_exception
            
# #         user_id = payload.get("sub")
# #         if user_id is None:
# #             raise credentials_exception
            
# #     except Exception:
# #         raise credentials_exception

# #     # Get user from database
# #     user = db.query(User).filter(User.id == int(user_id)).first()
# #     if user is None:
# #         raise credentials_exception
    
# #     return user

# # ---------- Current User ----------
# def get_current_user(
#     token: str = Depends(oauth2_scheme),
#     db: Session = Depends(get_db),
# ):
#     payload = verify_token(token)
#     if not payload:
#         raise HTTPException(status_code=401, detail="Invalid or expired token")
    
#     user_id = payload.get("sub")
#     role = payload.get("role")
    
#     try:
#         uid = int(user_id)
#     except Exception:
#         raise HTTPException(status_code=401, detail="Invalid token payload")

#     # Fetch based on role
#     if role in ["superadmin", "admin", "teacher"]:
#         user = db.query(User).filter(User.id == uid).first()
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")
#     elif role == "student":
#         user = db.query(Student).filter(Student.id == uid).first()
#         if not user:
#             raise HTTPException(status_code=404, detail="Student not found")
#     else:
#         raise HTTPException(status_code=403, detail="Unknown role")

#     # Attach role for later use
#     user.current_role = role
#     return user


# # ---------- Serialize User / Student ----------
# def serialize_user(user) -> dict:
#     """
#     Serializes User or Student object to standard response
#     """
#     if isinstance(user, User):
#         first_name = user.first_name or (user.name.split()[0] if user.name else None)
#         last_name = user.last_name or (user.name.split()[1] if user.name and len(user.name.split()) > 1 else None)
#         return {
#             "id": user.id,
#             "name": user.name,
#             "first_name": first_name,
#             "last_name": last_name,
#             "email": user.email,
#             "role": user.role.value,
#             "mobile": str(user.mobile) if user.mobile else None,
#         }
#     elif isinstance(user, Student):
#         return {
#             "id": user.id,
#             "name": f"{user.first_name} {user.last_name}".strip(),
#             "first_name": user.first_name,
#             "last_name": user.last_name,
#             "email": user.email,
#             "role": "student",
#             "mobile": str(user.mobile) if user.mobile else None,
#         }
#     else:
#         raise HTTPException(status_code=500, detail="Unknown user type")


# # ---------- Role Hierarchy ----------
# role_hierarchy = {
#     "superadmin": ["admin", "teacher", "student"],
#     "admin": ["teacher", "student"], 
#     "teacher": ["student"],
#     "student": []
# }

# def can_create_role(requester_role: str, target_role: str):
#     """Check if requester can create target role"""
#     return target_role in role_hierarchy.get(requester_role, [])

# # ---------- Role-based Dependencies ----------
# def require_role(required_roles: list[str]):
#     """Dependency factory for role-based access control"""
#     def role_checker(current_user: User = Depends(get_current_user)):
#         if current_user.role.value not in required_roles:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail=f"Access denied. Required roles: {required_roles}"
#             )
#         return current_user
#     return role_checker

# # Convenience dependencies for common role checks
# require_superadmin = require_role(["superadmin"])
# require_admin_or_above = require_role(["superadmin", "admin"])
# require_teacher_or_above = require_role(["superadmin", "admin", "teacher"])


# utils/security.py
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from database import get_db
from models import User, RoleEnum
import os

# ---------------- Password Helpers ----------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a plain password"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


# ---------------- JWT / Auth Helpers ----------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

SECRET_KEY = os.getenv("JWT_SECRET", "supersecret")
ALGORITHM = "HS256"


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Decode JWT and fetch the current user from DB"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user


def require_role(allowed_roles: list[RoleEnum]):
    """
    Dependency to check if the current user has one of the allowed roles.
    Usage:
        @router.post("/", dependencies=[Depends(require_role([RoleEnum.admin]))])
    """
    def role_checker(user: User = Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required roles: {[r.value for r in allowed_roles]}",
            )
        return user

    return role_checker

def require_superadmin(user: User = Depends(get_current_user)):
    if user.role != RoleEnum.superadmin:
        raise HTTPException(
            status_code=403,
            detail="Permission denied. Superadmin access only."
        )
    return user