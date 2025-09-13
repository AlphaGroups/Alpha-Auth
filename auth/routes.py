# # routers/auth.py
# from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from pydantic import BaseModel, EmailStr, Field
# from sqlalchemy.orm import Session
# import os
# from typing import Optional, List
# from datetime import timedelta

# from dotenv import load_dotenv
# load_dotenv()

# from database import get_db, SessionLocal
# from models import User, RoleEnum
# from utils.security import hash_password, verify_password
# from utils.token import generate_reset_token, verify_reset_token
# from app.templates import render_template
# from utils.sendgrid_email import send_email
# from auth.jwt import create_access_token, verify_token

# router = APIRouter(prefix="/auth", tags=["Auth"])

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# # Token expiry from env (fallback to sensible defaults)
# try:
#     ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
# except Exception:
#     ACCESS_TOKEN_EXPIRE_MINUTES = 15

# try:
#     REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
# except Exception:
#     REFRESH_TOKEN_EXPIRE_DAYS = 7

# # ---------- DB Dependency ----------
# def get_db_session():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # ---------- SCHEMAS ----------
# class RegisterInput(BaseModel):
#     first_name: str = Field(..., min_length=1)
#     last_name: str = Field(..., min_length=1)
#     email: EmailStr
#     mobile: Optional[str] = None                 # <-- changed to string
#     password: str = Field(..., min_length=6)
#     confirm_password: str = Field(..., min_length=6)
#     role: RoleEnum

# class LoginInput(BaseModel):
#     email: EmailStr
#     password: str

# class TokenResponse(BaseModel):
#     access_token: str
#     refresh_token: str
#     token_type: str

# class UserResponse(BaseModel):
#     id: int
#     name: Optional[str] = None
#     first_name: Optional[str] = None
#     last_name: Optional[str] = None
#     email: EmailStr
#     role: RoleEnum
#     mobile: Optional[str] = None                 # <-- string in response

#     # Pydantic v2 friendly setting (works with ORM attributes)
#     model_config = {"from_attributes": True}

# class ResetPasswordInput(BaseModel):
#     token: str
#     new_password: str

# class ForgotPasswordInput(BaseModel):
#     email: EmailStr

# # ---------- ROLE VALIDATION ----------
# def validate_role_assignment(requester_role: RoleEnum, new_role: RoleEnum):
#     if requester_role == RoleEnum.superadmin and new_role == RoleEnum.admin:
#         return True
#     if requester_role == RoleEnum.admin and new_role in [RoleEnum.teacher, RoleEnum.student]:
#         return True
#     if requester_role == RoleEnum.teacher and new_role == RoleEnum.student:
#         return True
#     raise HTTPException(status_code=403, detail="You are not allowed to create this role")

# # ---------- Superadmin Creation ----------
# def create_superadmin():
#     db = SessionLocal()
#     email = os.getenv("ADMIN_EMAIL")
#     if not email:
#         db.close()
#         return
#     existing = db.query(User).filter(User.email == email).first()
#     if not existing:
#         admin = User(
#             name=os.getenv("ADMIN_USER", "Super Admin"),
#             email=email,
#             hashed_password=hash_password(os.getenv("ADMIN_PASS", "admin123")),
#             role=RoleEnum.superadmin
#         )
#         # set mobile if model has it
#         if hasattr(admin, "mobile"):
#             admin.mobile = None
#         db.add(admin)
#         db.commit()
#         print(f"Superadmin {email} created")
#     db.close()

# # ---------- Helpers ----------
# def build_token_pair(user: User) -> dict:
#     access_token = create_access_token(
#         {"sub": str(user.id), "email": user.email, "role": user.role.value},
#         expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     )
#     refresh_token = create_access_token(
#         {"sub": str(user.id)},
#         expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
#     )
#     return {
#         "access_token": access_token,
#         "refresh_token": refresh_token,
#         "token_type": "bearer",
#     }

# def serialize_user(user: User) -> dict:
#     uid = getattr(user, "id", None)
#     email = getattr(user, "email", None)
#     name = getattr(user, "name", None)

#     first_name = getattr(user, "first_name", None)
#     last_name = getattr(user, "last_name", None)
#     if not first_name and name:
#         parts = name.strip().split()
#         if parts:
#             first_name = parts[0]
#             last_name = " ".join(parts[1:]) if len(parts) > 1 else None

#     # coerce mobile to string if present
#     raw_mobile = getattr(user, "mobile", None)
#     mobile = str(raw_mobile) if raw_mobile is not None else None

#     role_attr = getattr(user, "role", None)
#     role_value = role_attr.value if hasattr(role_attr, "value") else role_attr

#     return {
#         "id": uid,
#         "name": name,
#         "first_name": first_name,
#         "last_name": last_name,
#         "email": email,
#         "role": role_value,
#         "mobile": mobile,
#     }

# # ---------- OAuth2 / Swagger Login ----------
# @router.post("/token", response_model=TokenResponse)
# def login_for_access_token(
#     form_data: OAuth2PasswordRequestForm = Depends(),
#     db: Session = Depends(get_db_session)
# ):
#     user = db.query(User).filter(User.email == form_data.username).first()
#     if not user or not verify_password(form_data.password, user.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     return build_token_pair(user)

# # ---------- JSON Login Endpoint ----------
# @router.post("/login", response_model=TokenResponse)
# def login(data: LoginInput, db: Session = Depends(get_db_session)):
#     user = db.query(User).filter(User.email == data.email).first()
#     if not user or not verify_password(data.password, user.hashed_password):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
#     return build_token_pair(user)

# # ---------- Current User ----------
# def get_current_user(
#     token: str = Depends(oauth2_scheme),
#     db: Session = Depends(get_db_session),
# ):
#     payload = verify_token(token)
#     if not payload:
#         raise HTTPException(status_code=401, detail="Invalid or expired token")
#     user_id = payload.get("sub")
#     try:
#         uid = int(user_id)
#     except Exception:
#         raise HTTPException(status_code=401, detail="Invalid token payload")

#     user = db.query(User).filter(User.id == uid).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user

# # ----------- User Profile -----------
# @router.get("/profile", response_model=UserResponse)
# def read_users_me(current_user: User = Depends(get_current_user)):
#     return serialize_user(current_user)

# # ---------- Refresh Token ----------
# @router.post("/refresh", response_model=TokenResponse)
# def refresh_token(refresh_token: str = Body(..., embed=True), db: Session = Depends(get_db_session)):
#     payload = verify_token(refresh_token)
#     if payload is None:
#         raise HTTPException(status_code=401, detail="Invalid refresh token")
#     user_id = payload.get("sub")
#     try:
#         uid = int(user_id)
#     except Exception:
#         raise HTTPException(status_code=401, detail="Invalid token payload")
#     user = db.query(User).filter(User.id == uid).first()
#     if not user:
#         raise HTTPException(status_code=401, detail="User not found")
#     return build_token_pair(user)

# # ---------- Register ----------
# @router.post("/register", response_model=UserResponse)
# def register(data: RegisterInput, db: Session = Depends(get_db_session), current_user: User = Depends(lambda: None)):
#     if data.password != data.confirm_password:
#         raise HTTPException(status_code=400, detail="Passwords do not match")

#     existing_user = db.query(User).filter(User.email == data.email).first()
#     if existing_user:
#         raise HTTPException(status_code=400, detail="User already exists")

#     if current_user:
#         validate_role_assignment(current_user.role, data.role)

#     full_name = f"{data.first_name.strip()} {data.last_name.strip()}".strip()
#     new_user = User(
#         name=full_name,
#         first_name=data.first_name.strip(),
#         last_name=data.last_name.strip(),
#         email=data.email,
#         mobile=(str(data.mobile).strip() if data.mobile else None),
#         hashed_password=hash_password(data.password),
#         role=data.role,
#     )
#     # Coerce and set mobile as string if present and model supports it
#     if data.mobile is not None:
#         mobile_str = str(data.mobile).strip()
#         if hasattr(new_user, "mobile"):
#             new_user.mobile = mobile_str

#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return serialize_user(new_user)

# # ---------- CRUD ----------
# @router.get("/users/{id}", response_model=UserResponse)
# def get_user(id: int, db: Session = Depends(get_db_session), current_user: User = Depends(get_current_user)):
#     user = db.query(User).filter(User.id == id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return serialize_user(user)

# @router.get("/users", response_model=List[UserResponse])
# def get_all_users(db: Session = Depends(get_db_session), current_user: User = Depends(get_current_user)):
#     users = db.query(User).all()
#     return [serialize_user(u) for u in users]

# # ---------- Password Reset ----------
# @router.post("/forgot-password")
# async def forgot_password(data: ForgotPasswordInput, request: Request, db: Session = Depends(get_db_session)):
#     user = db.query(User).filter(User.email == data.email).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     token = generate_reset_token(user.email)
#     domain = request.base_url.hostname or "localhost"
#     html = render_template("forgot_password_notification.html", first_name=(getattr(user,"first_name",None) or (getattr(user,"name","").split()[0] if getattr(user,"name",None) else "")), token=token, domain=domain)
#     success = send_email(to_email=user.email, subject="Reset Your Password", html=html)
#     if not success:
#         raise HTTPException(status_code=500, detail="Failed to send email")
#     return {"message": "Reset link sent to email"}

# @router.post("/reset-password")
# def reset_password(data: ResetPasswordInput, db: Session = Depends(get_db_session)):
#     email = verify_reset_token(data.token)
#     if not email:
#         raise HTTPException(status_code=400, detail="Invalid or expired token")
#     user = db.query(User).filter(User.email == email).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     user.hashed_password = hash_password(data.new_password)
#     db.commit()
#     return {"message": "Password has been reset successfully"}


# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import timedelta
import os
import asyncio

from dotenv import load_dotenv
load_dotenv()

from database import get_db, ENV
from models import User, RoleEnum
from utils.security import hash_password, verify_password
from utils.token import generate_reset_token, verify_reset_token
from app.templates import render_template
from utils.sendgrid_email import send_email
from auth.jwt import create_access_token, verify_token

router = APIRouter(prefix="/auth", tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Token expiry
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# ---------- SCHEMAS ----------
class RegisterInput(BaseModel):
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    email: EmailStr
    mobile: Optional[str] = None
    password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)
    role: RoleEnum

class LoginInput(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class UserResponse(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr
    role: RoleEnum
    mobile: Optional[str] = None
    model_config = {"from_attributes": True}

class ResetPasswordInput(BaseModel):
    token: str
    new_password: str

class ForgotPasswordInput(BaseModel):
    email: EmailStr

# ---------- HELPERS ----------
def build_token_pair(user: dict) -> dict:
    access_token = create_access_token(
        {"sub": str(user.get("id")), "email": user.get("email"), "role": user.get("role")},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_access_token(
        {"sub": str(user.get("id"))},
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

def serialize_user(user) -> dict:
    if ENV == "development":  # SQLAlchemy
        uid = getattr(user, "id", None)
        email = getattr(user, "email", None)
        name = getattr(user, "name", None)
        first_name = getattr(user, "first_name", None)
        last_name = getattr(user, "last_name", None)
        if not first_name and name:
            parts = name.strip().split()
            first_name = parts[0]
            last_name = " ".join(parts[1:]) if len(parts) > 1 else None
        mobile = str(getattr(user, "mobile", None)) if getattr(user, "mobile", None) else None
        role = getattr(user, "role").value if hasattr(getattr(user, "role"), "value") else getattr(user, "role")
    else:  # MongoDB
        uid = user.get("_id")
        email = user.get("email")
        name = user.get("name")
        first_name = user.get("first_name")
        last_name = user.get("last_name")
        mobile = str(user.get("mobile")) if user.get("mobile") else None
        role = user.get("role")
    return {"id": uid, "email": email, "name": name, "first_name": first_name, "last_name": last_name, "mobile": mobile, "role": role}

# ---------- LOGIN ----------
@router.post("/login", response_model=TokenResponse)
async def login(data: LoginInput, db=Depends(get_db)):
    if ENV == "development":
        user = db.query(User).filter(User.email == data.email).first()
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return build_token_pair(serialize_user(user))
    else:  # MongoDB
        user = await db["users"].find_one({"email": data.email})
        if not user or not verify_password(data.password, user.get("hashed_password")):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return build_token_pair(user)

# ---------- REGISTER ----------
@router.post("/register", response_model=UserResponse)
async def register(data: RegisterInput, db=Depends(get_db)):
    if data.password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    if ENV == "development":
        existing = db.query(User).filter(User.email == data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="User already exists")
        full_name = f"{data.first_name.strip()} {data.last_name.strip()}"
        new_user = User(
            name=full_name,
            first_name=data.first_name.strip(),
            last_name=data.last_name.strip(),
            email=data.email,
            mobile=(str(data.mobile).strip() if data.mobile else None),
            hashed_password=hash_password(data.password),
            role=data.role
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return serialize_user(new_user)
    else:
        existing = await db["users"].find_one({"email": data.email})
        if existing:
            raise HTTPException(status_code=400, detail="User already exists")
        user_dict = {
            "name": f"{data.first_name} {data.last_name}",
            "first_name": data.first_name,
            "last_name": data.last_name,
            "email": data.email,
            "mobile": str(data.mobile) if data.mobile else None,
            "hashed_password": hash_password(data.password),
            "role": data.role.value
        }
        result = await db["users"].insert_one(user_dict)
        user_dict["_id"] = result.inserted_id
        return serialize_user(user_dict)
