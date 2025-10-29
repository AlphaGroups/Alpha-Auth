from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from auth.routes import router as auth_router
from database import Base, engine, SessionLocal
from app.routes.video_routes import router as video_router  
from models import User, RoleEnum, Class   # ✅ Import Class model
from utils.security import hash_password
from utils.class_seeder import seed_classes
import os

from app.routes.admin import router as admin_router
from app.routes.adminaccess import router as adminvideos_router
from app.routes.teacher import router as teacher_router
from app.routes.student import router as student_router
from app.routes.college import router as college_router

# Import email functionality
from utils.email_service import send_email

# Load environment variables based on environment
if os.getenv("APP_ENV") == "production":
    # In production, environment variables are set by Render directly
    # So we don't need to load from .env file
    pass
else:
    # For development, load from .env.development
    load_dotenv(".env.development")

app = FastAPI()

# Include routes
app.include_router(auth_router)
app.include_router(video_router)
app.include_router(teacher_router)
app.include_router(admin_router)
app.include_router(college_router)
app.include_router(student_router)
app.include_router(adminvideos_router)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # local dev
        "https://alpha-auth.onrender.com",
        "https://monorepo-web-liard-six.vercel.app",  # production frontend
        "https://monorepo-lms.vercel.app",
        "https://alphagroups.co.in",
        "https://lively-rock-0d84cff1e.3.azurestaticapps.net"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Startup event ----------
@app.on_event("startup")
def startup_tasks():
    # Create DB tables if not exist (moved from global execution to startup event)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # ✅ 1. Create superadmin if not exists
        admin_email = os.getenv("ADMIN_EMAIL")
        admin_pass = os.getenv("ADMIN_PASS")
        admin_user = os.getenv("ADMIN_USER", "Super Admin")
        admin_mobile = os.getenv("ADMIN_MOBILE", "")

        if admin_email and admin_pass:
            existing = db.query(User).filter(User.email == admin_email).first()
            if not existing:
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
                    mobile=admin_mobile  # Add mobile if available
                )
                db.add(superadmin)
                db.commit()
                print("✅ Superadmin created:", admin_email)
                
                # Send welcome email to the admin
                try:
                    html_content = f"""
                    <html>
                    <body>
                        <h2>Welcome to Alpha Groups, {first_name}!</h2>
                        <p>Your superadmin account has been successfully created.</p>
                        <p><strong>Account Details:</strong></p>
                        <ul>
                            <li><strong>Email:</strong> {admin_email}</li>
                            <li><strong>Role:</strong> Super Admin</li>
                            <li><strong>Temporary Password:</strong> {admin_pass}</li>
                        </ul>
                        <p>Please change your password after your first login for security.</p>
                        <p>Thank you for using Alpha Groups platform!</p>
                    </body>
                    </html>
                    """
                    
                    plain_text = f"""
                    Welcome to Alpha Groups, {first_name}!
                    
                    Your superadmin account has been successfully created.
                    
                    Account Details:
                    - Email: {admin_email}
                    - Role: Super Admin
                    - Temporary Password: {admin_pass}
                    
                    Please change your password after your first login for security.
                    Thank you for using Alpha Groups platform!
                    """
                    
                    success = send_email(
                        to_email=admin_email,
                        subject="Welcome - Super Admin Account Created",
                        html=html_content,
                        plain_text=plain_text
                    )
                    
                    if success:
                        print(f"✅ Welcome email sent to admin: {admin_email}")
                    else:
                        print(f"❌ Failed to send welcome email to admin: {admin_email}")
                        
                except Exception as e:
                    print(f"❌ Error sending welcome email: {str(e)}")
                    
            else:
                print("ℹ️ Superadmin already exists:", admin_email)
        else:
            print("⚠️ ADMIN_EMAIL or ADMIN_PASS not set in .env")

        # ✅ 2. Seed Classes (1–12) using utility function
        seed_classes()

    finally:
        db.close()
