from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from auth.routes import router as auth_router
from database import Base, engine, SessionLocal
from app.routes.video_routes import router as video_router  
from models import User, RoleEnum
from utils.security import hash_password
import os

from app.routes.admin import router as admin_router
from app.routes.adminaccess import router as adminvideos_router

from app.routes.teacher import router as teacher_router
from app.routes.student import router as student_router

from app.routes.college import router as college_router

# Load environment variables
load_dotenv()

# Create DB tables if not exist
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include auth routes
app.include_router(auth_router)
app.include_router(video_router)
app.include_router(teacher_router)
app.include_router(admin_router)
app.include_router(college_router)
app.include_router(student_router)
app.include_router(adminvideos_router)


# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # local dev
        "https://alpha-auth.onrender.com",
        "https://monorepo-web-liard-six.vercel.app",  # production frontend
        "https://monorepo-lms.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Startup event to create superadmin ----------
@app.on_event("startup")
def create_superadmin():
    db = SessionLocal()
    try:
        admin_email = os.getenv("ADMIN_EMAIL")
        admin_pass = os.getenv("ADMIN_PASS")
        admin_user = os.getenv("ADMIN_USER", "Super Admin")

        if not admin_email or not admin_pass:
            print("⚠️ ADMIN_EMAIL or ADMIN_PASS not set in .env")
            return

        existing = db.query(User).filter(User.email == admin_email).first()
        if not existing:
            # Split full name into first and last name
            parts = admin_user.strip().split()
            first_name = parts[0]
            last_name = " ".join(parts[1:]) if len(parts) > 1 else None
        
            superadmin = User(
                name=admin_user,
                first_name=first_name,
                last_name=last_name,
                email=admin_email,
                hashed_password=hash_password(admin_pass),
                role=RoleEnum.superadmin,
            )
            db.add(superadmin)
            db.commit()
            print("✅ Superadmin created:", admin_email)

        else:
            print("ℹ️ Superadmin already exists:", admin_email)
    finally:
        db.close()
