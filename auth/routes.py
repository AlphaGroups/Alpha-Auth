# from fastapi import APIRouter, Depends, HTTPException, status, Request
# from pydantic import BaseModel, EmailStr
# from sqlalchemy.orm import Session

# from auth.jwt import create_access_token, get_current_user
# from database import SessionLocal
# from models import User, RoleEnum
# from utils.security import hash_password, verify_password
# from utils.token import generate_reset_token, verify_reset_token
# from app.templates import render_template
# from utils.sendgrid_email import send_email

# router = APIRouter()
# router = APIRouter(prefix="/auth", tags=["Auth"])

# # ---------- DB Dependency ----------
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# # ---------- SCHEMAS ----------
# class RegisterInput(BaseModel):
#     name: str
#     email: EmailStr
#     password: str
#     role: RoleEnum  # <-- explicitly choose role


# class LoginInput(BaseModel):
#     email: EmailStr
#     password: str


# class LoginResponse(BaseModel):
#     accessToken: str


# class UserResponse(BaseModel):
#     id: int
#     name: str
#     email: EmailStr
#     role: RoleEnum

#     class Config:
#         orm_mode = True


# class ResetPasswordInput(BaseModel):
#     token: str
#     new_password: str


# class ForgotPasswordInput(BaseModel):
#     email: EmailStr


# # ---------- ROLE VALIDATION ----------
# def validate_role_assignment(requester_role: RoleEnum, new_role: RoleEnum):
#     """Ensure hierarchy is respected"""
#     if requester_role == RoleEnum.superadmin and new_role == RoleEnum.admin:
#         return True
#     if requester_role == RoleEnum.admin and new_role in [RoleEnum.teacher, RoleEnum.student]:
#         return True
#     if requester_role == RoleEnum.teacher and new_role == RoleEnum.student:
#         return True
#     raise HTTPException(status_code=403, detail="You are not allowed to create this role")



# @router.post("/refresh")
# def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
#     payload = verify_token(refresh_token, refresh=True)
#     if payload is None:
#         raise HTTPException(status_code=401, detail="Invalid refresh token")
    
#     user_id = payload.get("sub")
#     user = db.query(User).filter(User.id == int(user_id)).first()
#     if not user:
#         raise HTTPException(status_code=401, detail="User not found")
    
#     # Issue new access token
#     new_access = create_access_token({"sub": str(user.id), "role": user.role})
#     return {"access_token": new_access, "token_type": "bearer"}

# # ---------- AUTH ROUTES ----------
# @router.post("/register", response_model=UserResponse)
# def register(
#     data: RegisterInput,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     # Check if email already exists
#     existing_user = db.query(User).filter(User.email == data.email).first()
#     if existing_user:
#         raise HTTPException(status_code=400, detail="User already exists")

#     # Validate role creation based on hierarchy
#     validate_role_assignment(current_user.role, data.role)

#     # Create new user
#     new_user = User(
#         name=data.name,
#         email=data.email,
#         hashed_password=hash_password(data.password),
#         role=data.role,
#     )
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)

#     return new_user


# class LoginInput(BaseModel):
#     email: EmailStr
#     password: str

# class LoginResponse(BaseModel):
#     accessToken: str

# @router.post("/login", response_model=LoginResponse)
# def login(data: LoginInput, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.email == data.email).first()
#     if not user or not verify_password(data.password, user.hashed_password):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

#     token = create_access_token({
#         "sub": str(user.id),
#         "email": user.email,
#         "role": user.role.value,
#     })

#     return {"accessToken": token}


# @router.post("/forgot-password")
# async def forgot_password(data: ForgotPasswordInput, request: Request, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.email == data.email).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     token = generate_reset_token(user.email)
#     domain = request.base_url.hostname or "localhost"

#     html = render_template(
#         "forgot_password_notification.html",
#         first_name=user.name.split()[0],
#         token=token,
#         domain=domain,
#     )

#     subject = "Reset Your Password"
#     success = send_email(to_email=user.email, subject=subject, html=html)

#     if not success:
#         raise HTTPException(status_code=500, detail="Failed to send email")

#     return {"message": "Reset link sent to email"}


# @router.post("/reset-password")
# def reset_password(data: ResetPasswordInput, db: Session = Depends(get_db)):
#     email = verify_reset_token(data.token)
#     if not email:
#         raise HTTPException(status_code=400, detail="Invalid or expired token")

#     user = db.query(User).filter(User.email == email).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     user.hashed_password = hash_password(data.new_password)
#     db.commit()

#     return {"message": "Password has been reset successfully"}


# # ---------- CRUD ROUTES ----------
# @router.get("/users/{id}", response_model=UserResponse)
# def get_user(id: int, db: Session = Depends(get_db)):
#     user = db.query(User).get(id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user


# @router.get("/users", response_model=list[UserResponse])
# def get_all_users(db: Session = Depends(get_db)):
#     return db.query(User).all()


# @router.put("/users/{id}", response_model=UserResponse)
# def update_user(id: int, data: RegisterInput, db: Session = Depends(get_db)):
#     user = db.query(User).get(id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     user.name = data.name
#     user.email = data.email
#     user.hashed_password = hash_password(data.password)
#     user.role = data.role

#     db.commit()
#     db.refresh(user)
#     return user


# @router.delete("/users/{id}")
# def delete_user(id: int, db: Session = Depends(get_db)):
#     user = db.query(User).get(id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     db.delete(user)
#     db.commit()
#     return {"message": f"User {id} deleted successfully"}




# from fastapi import APIRouter, Depends, HTTPException, status, Request
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from pydantic import BaseModel, EmailStr
# from sqlalchemy.orm import Session

# from auth.jwt import create_access_token, get_current_user, verify_token  # ✅ Added verify_token import
# from database import SessionLocal
# from models import User, RoleEnum
# from utils.security import hash_password, verify_password
# from utils.token import generate_reset_token, verify_reset_token
# from app.templates import render_template
# from utils.sendgrid_email import send_email

# router = APIRouter(prefix="/auth", tags=["Auth"])

# # ✅ OAuth2 scheme for Swagger authentication
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# # ---------- DB Dependency ----------
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# # ---------- SCHEMAS ----------
# class RegisterInput(BaseModel):
#     name: str
#     email: EmailStr
#     password: str
#     role: RoleEnum  # <-- explicitly choose role


# class LoginInput(BaseModel):
#     email: EmailStr
#     password: str


# class LoginResponse(BaseModel):
#     access_token: str  # ✅ Changed from accessToken to access_token for OAuth2 compliance
#     token_type: str


# class UserResponse(BaseModel):
#     id: int
#     name: str
#     email: EmailStr
#     role: RoleEnum

#     class Config:
#         orm_mode = True


# class ResetPasswordInput(BaseModel):
#     token: str
#     new_password: str


# class ForgotPasswordInput(BaseModel):
#     email: EmailStr


# # ---------- ROLE VALIDATION ----------
# def validate_role_assignment(requester_role: RoleEnum, new_role: RoleEnum):
#     """Ensure hierarchy is respected"""
#     if requester_role == RoleEnum.superadmin and new_role == RoleEnum.admin:
#         return True
#     if requester_role == RoleEnum.admin and new_role in [RoleEnum.teacher, RoleEnum.student]:
#         return True
#     if requester_role == RoleEnum.teacher and new_role == RoleEnum.student:
#         return True
#     raise HTTPException(status_code=403, detail="You are not allowed to create this role")


# # ✅ OAuth2 compatible token endpoint for Swagger
# @router.post("/token", response_model=LoginResponse)
# def login_for_access_token(
#     form_data: OAuth2PasswordRequestForm = Depends(), 
#     db: Session = Depends(get_db)
# ):
#     """OAuth2 compatible login endpoint for Swagger UI"""
#     user = db.query(User).filter(User.email == form_data.username).first()
#     if not user or not verify_password(form_data.password, user.hashed_password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )

#     token = create_access_token({
#         "sub": str(user.id),
#         "email": user.email,
#         "role": user.role.value,
#     })

#     return {
#         "access_token": token,
#         "token_type": "bearer"
#     }


# @router.post("/refresh")
# def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
#     payload = verify_token(refresh_token, refresh=True)
#     if payload is None:
#         raise HTTPException(status_code=401, detail="Invalid refresh token")
    
#     user_id = payload.get("sub")
#     user = db.query(User).filter(User.id == int(user_id)).first()
#     if not user:
#         raise HTTPException(status_code=401, detail="User not found")
    
#     # Issue new access token
#     new_access = create_access_token({"sub": str(user.id), "role": user.role})
#     return {"access_token": new_access, "token_type": "bearer"}


# # ---------- AUTH ROUTES ----------
# @router.post("/register", response_model=UserResponse)
# def register(
#     data: RegisterInput,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     # Check if email already exists
#     existing_user = db.query(User).filter(User.email == data.email).first()
#     if existing_user:
#         raise HTTPException(status_code=400, detail="User already exists")

#     # Validate role creation based on hierarchy
#     validate_role_assignment(current_user.role, data.role)

#     # Create new user
#     new_user = User(
#         name=data.name,
#         email=data.email,
#         hashed_password=hash_password(data.password),
#         role=data.role,
#     )
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)

#     return new_user


# # ✅ Keep the original login endpoint for JSON requests
# @router.post("/login", response_model=LoginResponse)
# def login(data: LoginInput, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.email == data.email).first()
#     if not user or not verify_password(data.password, user.hashed_password):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

#     token = create_access_token({
#         "sub": str(user.id),
#         "email": user.email,
#         "role": user.role.value,
#     })

#     return {
#         "access_token": token,
#         "token_type": "bearer"
#     }


# @router.post("/forgot-password")
# async def forgot_password(data: ForgotPasswordInput, request: Request, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.email == data.email).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     token = generate_reset_token(user.email)
#     domain = request.base_url.hostname or "localhost"

#     html = render_template(
#         "forgot_password_notification.html",
#         first_name=user.name.split()[0],
#         token=token,
#         domain=domain,
#     )

#     subject = "Reset Your Password"
#     success = send_email(to_email=user.email, subject=subject, html=html)

#     if not success:
#         raise HTTPException(status_code=500, detail="Failed to send email")

#     return {"message": "Reset link sent to email"}


# @router.post("/reset-password")
# def reset_password(data: ResetPasswordInput, db: Session = Depends(get_db)):
#     email = verify_reset_token(data.token)
#     if not email:
#         raise HTTPException(status_code=400, detail="Invalid or expired token")

#     user = db.query(User).filter(User.email == email).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     user.hashed_password = hash_password(data.new_password)
#     db.commit()

#     return {"message": "Password has been reset successfully"}


# # ---------- CRUD ROUTES ----------
# @router.get("/users/{id}", response_model=UserResponse)
# def get_user(
#     id: int, 
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)  # ✅ Added authentication
# ):
#     user = db.query(User).get(id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user


# @router.get("/users", response_model=list[UserResponse])
# def get_all_users(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)  # ✅ Added authentication
# ):
#     return db.query(User).all()


# @router.put("/users/{id}", response_model=UserResponse)
# def update_user(
#     id: int, 
#     data: RegisterInput, 
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)  # ✅ Added authentication
# ):
#     user = db.query(User).get(id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     # ✅ Validate role update permissions
#     if data.role != user.role:  # Only validate if role is changing
#         validate_role_assignment(current_user.role, data.role)

#     user.name = data.name
#     user.email = data.email
#     if data.password:  # ✅ Only update password if provided
#         user.hashed_password = hash_password(data.password)
#     user.role = data.role

#     db.commit()
#     db.refresh(user)
#     return user


# @router.delete("/users/{id}")
# def delete_user(
#     id: int, 
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)  # ✅ Added authentication
# ):
#     user = db.query(User).get(id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     # ✅ Prevent self-deletion
#     if user.id == current_user.id:
#         raise HTTPException(status_code=400, detail="Cannot delete yourself")

#     db.delete(user)
#     db.commit()
#     return {"message": f"User {id} deleted successfully"}

# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
import os

from database import get_db, SessionLocal
from models import User, RoleEnum
from utils.security import hash_password, verify_password
from utils.token import generate_reset_token, verify_reset_token
from app.templates import render_template
from utils.sendgrid_email import send_email
from auth.jwt import create_access_token, verify_token

router = APIRouter(prefix="/auth", tags=["Auth"])

# OAuth2 scheme for Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# ---------- DB Dependency ----------
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- SCHEMAS ----------
class RegisterInput(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: RoleEnum

class LoginInput(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: RoleEnum
    class Config:
        orm_mode = True

class ResetPasswordInput(BaseModel):
    token: str
    new_password: str

class ForgotPasswordInput(BaseModel):
    email: EmailStr

# ---------- ROLE VALIDATION ----------
def validate_role_assignment(requester_role: RoleEnum, new_role: RoleEnum):
    if requester_role == RoleEnum.superadmin and new_role == RoleEnum.admin:
        return True
    if requester_role == RoleEnum.admin and new_role in [RoleEnum.teacher, RoleEnum.student]:
        return True
    if requester_role == RoleEnum.teacher and new_role == RoleEnum.student:
        return True
    raise HTTPException(status_code=403, detail="You are not allowed to create this role")

# ---------- Superadmin Creation ----------
def create_superadmin():
    db = SessionLocal()
    email = os.getenv("ADMIN_EMAIL")
    existing = db.query(User).filter(User.email == email).first()
    if not existing:
        admin = User(
            name=os.getenv("ADMIN_USER"),
            email=email,
            hashed_password=hash_password(os.getenv("ADMIN_PASS")),
            role=RoleEnum.superadmin
        )
        db.add(admin)
        db.commit()
        print(f"Superadmin {email} created")
    db.close()

# ---------- OAuth2 / Swagger Login ----------
@router.post("/token", response_model=LoginResponse)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db_session)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role.value})
    return {"access_token": token, "token_type": "bearer"}

# ---------- JSON Login Endpoint ----------
@router.post("/login", response_model=LoginResponse)
def login(data: LoginInput, db: Session = Depends(get_db_session)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role.value})
    return {"access_token": token, "token_type": "bearer"}

# ---------- Refresh Token ----------
@router.post("/refresh")
def refresh_token(refresh_token: str, db: Session = Depends(get_db_session)):
    payload = verify_token(refresh_token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    new_access = create_access_token({"sub": str(user.id), "role": user.role.value})
    return {"access_token": new_access, "token_type": "bearer"}

# ---------- Register ----------
@router.post("/register", response_model=UserResponse)
def register(data: RegisterInput, db: Session = Depends(get_db_session), current_user: User = Depends(lambda: None)):
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    # Only validate role if current_user exists
    if current_user:
        validate_role_assignment(current_user.role, data.role)
    new_user = User(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# ---------- CRUD ----------
@router.get("/users/{id}", response_model=UserResponse)
def get_user(id: int, db: Session = Depends(get_db_session), current_user: User = Depends(oauth2_scheme)):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/users", response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db_session), current_user: User = Depends(oauth2_scheme)):
    return db.query(User).all()

# ---------- Password Reset ----------
@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordInput, request: Request, db: Session = Depends(get_db_session)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token = generate_reset_token(user.email)
    domain = request.base_url.hostname or "localhost"
    html = render_template("forgot_password_notification.html", first_name=user.name.split()[0], token=token, domain=domain)
    success = send_email(to_email=user.email, subject="Reset Your Password", html=html)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send email")
    return {"message": "Reset link sent to email"}

@router.post("/reset-password")
def reset_password(data: ResetPasswordInput, db: Session = Depends(get_db_session)):
    email = verify_reset_token(data.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.hashed_password = hash_password(data.new_password)
    db.commit()
    return {"message": "Password has been reset successfully"}
