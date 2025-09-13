# from fastapi import FastAPI
# from dotenv import load_dotenv
# from auth.routes import router as auth_router
# from database import Base, engine, SessionLocal
# from fastapi.middleware.cors import CORSMiddleware
# from models import User, RoleEnum
# from utils.security import hash_password
# import os

# # Load environment variables
# load_dotenv()

# # Create DB tables
# Base.metadata.create_all(bind=engine)

# app = FastAPI()

# # Include auth routes
# app.include_router(auth_router)

# # Enable CORS for frontend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ---------- Startup event ----------
# @app.on_event("startup")
# def create_superadmin():
#     db = SessionLocal()
#     try:
#         admin_email = os.getenv("ADMIN_EMAIL")
#         admin_pass = os.getenv("ADMIN_PASS")
#         admin_user = os.getenv("ADMIN_USER")

#         existing = db.query(User).filter(User.email == admin_email).first()
#         if not existing:
#             superadmin = User(
#                 name=admin_user,
#                 email=admin_email,
#                 hashed_password=hash_password(admin_pass),  # 👈 using hash_password
#                 role=RoleEnum.superadmin,
#             )
#             db.add(superadmin)
#             db.commit()
#             print("✅ Superadmin created:", admin_email)
#         else:
#             print("ℹ️ Superadmin already exists:", admin_email)
#     finally:
#         db.close()



# main.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# load .env
load_dotenv()

# Prefer ENV (lowercase check later). Default to development to be safe.
ENV = os.getenv("ENV", os.getenv("APP_ENV", "development")).lower()

# Import router and models/DB handles in a way that doesn't fail at import time
from auth.routes import router as auth_router
from models import User, RoleEnum
from utils.security import hash_password

# Import DB objects (some may be None depending on ENV)
from database import (
    # these names may be None if ENV == "production"
    engine,
    Base,
    SessionLocal,
    # and for mongo:
    mongo_db,
)

app = FastAPI()

# register routers
app.include_router(auth_router)

# CORS: allow your frontend origins (adjust as necessary)
origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# only create SQL tables in development (when engine/Base exist)
if ENV == "development" and engine is not None and Base is not None:
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ SQL tables created (development)")
    except Exception as e:
        print("⚠️ Failed to create SQL tables:", e)

# startup event: ensure superadmin exists (handles SQL and Mongo)
@app.on_event("startup")
async def create_superadmin():
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_pass = os.getenv("ADMIN_PASS")
    admin_user = os.getenv("ADMIN_USER", "superadmin")

    if not admin_email or not admin_pass:
        print("⚠️ ADMIN_EMAIL or ADMIN_PASS not set — skipping superadmin creation")
        return

    if ENV == "development":
        # SQLAlchemy synchronous path
        if SessionLocal is None:
            print("⚠️ SessionLocal not available — cannot create superadmin in dev")
            return
        db = SessionLocal()
        try:
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
                print("✅ Superadmin (SQL) created:", admin_email)
            else:
                print("ℹ️ Superadmin (SQL) already exists:", admin_email)
        except Exception as e:
            print("⚠️ Error ensuring SQL superadmin:", e)
        finally:
            db.close()
    else:
        # production -> Mongo (async)
        if mongo_db is None:
            print("⚠️ mongo_db is not initialized; check MONGO_URI")
            return

        users = mongo_db.get_collection("users")
        existing = await users.find_one({"email": admin_email})
        if not existing:
            user_doc = {
                "name": admin_user,
                "first_name": None,
                "last_name": None,
                "email": admin_email,
                "mobile": None,
                "hashed_password": hash_password(admin_pass),
                "role": RoleEnum.superadmin.value if hasattr(RoleEnum.superadmin, "value") else str(RoleEnum.superadmin),
            }
            res = await users.insert_one(user_doc)
            print("✅ Superadmin (Mongo) created:", admin_email, "id:", res.inserted_id)
        else:
            print("ℹ️ Superadmin (Mongo) already exists:", admin_email)
