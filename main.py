
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from auth.routes import router as auth_router

# app = FastAPI()

# # Include auth routes
# app.include_router(auth_router)

# # Enable CORS for frontend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:3000",  # local dev
#         "https://monorepo-web-liard-six.vercel.app"  # production frontend
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from auth.routes import router as auth_router
from database import Base, engine, SessionLocal
from app.routes.video_routes import router as video_router  
from models import User, RoleEnum
from utils.security import hash_password
import os
from app.routes.teacher import router as teacher_router
from app.routes.admin import router as admin_router
from app.routes.college import router as college_router
from app.routes.student import router as student_router

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


# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # local dev
        "https://monorepo-web-liard-six.vercel.app"  # production frontend
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
            superadmin = User(
                name=admin_user,
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
#
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from dotenv import load_dotenv
# from auth.routes import router as auth_router
# from app.routes.video_routes import router as video_router   # 👈 correct import
# from database import Base, engine, SessionLocal
# from models import User, RoleEnum
# from utils.security import hash_password
# import os

# # Load environment variables
# load_dotenv()

# # Create DB tables if not exist
# Base.metadata.create_all(bind=engine)

# app = FastAPI()

# # Include routers
# app.include_router(auth_router)
# app.include_router(video_router)   # 👈 include video routes

# # Enable CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:3000",
#         "https://monorepo-web-liard-six.vercel.app"
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Startup superadmin creation
# @app.on_event("startup")
# def create_superadmin():
#     db = SessionLocal()
#     try:
#         admin_email = os.getenv("ADMIN_EMAIL")
#         admin_pass = os.getenv("ADMIN_PASS")
#         admin_user = os.getenv("ADMIN_USER", "Super Admin")

#         if not admin_email or not admin_pass:
#             print("⚠️ ADMIN_EMAIL or ADMIN_PASS not set in .env")
#             return

#         existing = db.query(User).filter(User.email == admin_email).first()
#         if not existing:
#             superadmin = User(
#                 name=admin_user,
#                 email=admin_email,
#                 hashed_password=hash_password(admin_pass),
#                 role=RoleEnum.superadmin,
#             )
#             db.add(superadmin)
#             db.commit()
#             print("✅ Superadmin created:", admin_email)
#         else:
#             print("ℹ️ Superadmin already exists:", admin_email)
#     finally:
#         db.close()
