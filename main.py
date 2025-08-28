from fastapi import FastAPI
from dotenv import load_dotenv
from auth.routes import router as auth_router
from database import Base, engine, SessionLocal
from fastapi.middleware.cors import CORSMiddleware
from models import User, RoleEnum
from utils.security import hash_password
import os

# Load environment variables
load_dotenv()

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include auth routes
app.include_router(auth_router)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Startup event ----------
@app.on_event("startup")
def create_superadmin():
    db = SessionLocal()
    try:
        admin_email = os.getenv("ADMIN_EMAIL")
        admin_pass = os.getenv("ADMIN_PASS")
        admin_user = os.getenv("ADMIN_USER")

        existing = db.query(User).filter(User.email == admin_email).first()
        if not existing:
            superadmin = User(
                name=admin_user,
                email=admin_email,
                hashed_password=hash_password(admin_pass),  # 👈 using hash_password
                role=RoleEnum.superadmin,
            )
            db.add(superadmin)
            db.commit()
            print("✅ Superadmin created:", admin_email)
        else:
            print("ℹ️ Superadmin already exists:", admin_email)
    finally:
        db.close()
