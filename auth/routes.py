from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from auth.jwt import create_access_token
from database import SessionLocal
from models import User
from utils.security import hash_password, verify_password
from utils.reset_token import generate_reset_token, verify_reset_token

from app.templates import render_template
from utils.brevo_email import send_email
from utils.reset_token import generate_reset_token

router = APIRouter()

# ---------- DB Dependency ----------
def get_db():
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

class LoginInput(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    accessToken: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True

class ResetPasswordInput(BaseModel):
    token: str
    new_password: str

class ForgotPasswordInput(BaseModel):
    email: EmailStr

# ---------- AUTH ROUTES ----------
# @router.post("/auth/register")
# def register(data: RegisterInput, db: Session = Depends(get_db)):
#     existing_user = db.query(User).filter(User.email == data.email).first()
#     if existing_user:
#         raise HTTPException(status_code=400, detail="User already exists")

#     new_user = User(
#         name=data.name,
#         email=data.email,
#         hashed_password=hash_password(data.password)
#     )
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)

#      html = render_template(
#         "registeration.html",
#         first_name=user.name.split()[0],
#         token=token,
#         domain=domain,
#     )

#     return {"message": "User registered successfully"}
# ---------- AUTH ROUTES ----------
@router.post("/auth/register")
def register(data: RegisterInput, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # ✅ Generate token for this user
    token = create_access_token({
        "sub": str(new_user.id),
        "email": new_user.email,
        "role": "user"
    })

    # ✅ Define your domain (hardcoded or from settings)
    domain = "http://localhost:3000"

    # ✅ Render email HTML
    html = render_template(
        "registeration.html",
        first_name=new_user.name.split()[0],
        token=token,
        domain=domain,
    )

    # ✅ Send welcome email to new user
    subject = "Welcome to MI-ware - Account Created Successfully!"
    success = send_email(to_email=new_user.email, subject=subject, html=html)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send welcome email")

    return {"message": "User registered successfully"}

@router.post("/auth/login", response_model=LoginResponse)
def login(data: LoginInput, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "role": "user"
    })

    return {"accessToken": token}

@router.post("/auth/forgot-password")
async def forgot_password(data: ForgotPasswordInput, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = generate_reset_token(user.email)
    domain = request.base_url.hostname or "busybrains.ai"

    html = render_template(
        "forgot_password_notification.html",
        first_name=user.name.split()[0],
        token=token,
        domain=domain,
    )

    subject = "Reset Your Password – BusyBrains"
    success = send_email(to_email=user.email, subject=subject, html=html)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to send email")

    return {"message": "Reset link sent to email"}
    
# @router.post("/auth/forgot-password")
# async def forgot_password(data: ForgotPasswordInput, request: Request, db: Session = Depends(get_db)):
#     email = data.email
#     user = db.query(User).filter(User.email == email).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     token = generate_reset_token(email)
#     reset_link = f"{request.base_url}auth/reset-password/{token}"

#     subject = "Password Reset Request - FBOrganization"
#     body = f"""
# Hi {user.name},

# You requested to reset your password. Click the link below:

# {reset_link}

# If you did not request this, you can ignore this email.

# — FBOrganization Team
# """

#     from utils.sendgrid_email import send_email
#     success = send_email(email, subject, body)
#     if not success:
#         raise HTTPException(status_code=500, detail="Failed to send email")

#     return {"reset_link": reset_link, "message": "Reset link sent to email"}

    
@router.post("/auth/reset-password")
def reset_password(data: ResetPasswordInput, db: Session = Depends(get_db)):
    email = verify_reset_token(data.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = hash_password(data.new_password)
    db.commit()

    return {"message": "Password has been reset successfully"}

# ---------- CRUD ROUTES ----------
@router.get("/users/{id}", response_model=UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(User).get(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{id}", response_model=UserResponse)
def update_user(id: int, data: RegisterInput, db: Session = Depends(get_db)):
    user = db.query(User).get(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.name = data.name
    user.email = data.email
    user.hashed_password = hash_password(data.password)

    db.commit()
    db.refresh(user)
    return user

@router.delete("/users/{id}")
def delete_user(id: int, db: Session = Depends(get_db)):
    user = db.query(User).get(id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": f"User {id} deleted successfully"}

@router.get("/users", response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(User).all()
