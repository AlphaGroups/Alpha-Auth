from fastapi import FastAPI
from dotenv import load_dotenv
from auth.routes import router as auth_router  # ✅ path relative to root
from database import Base, engine
from models import User

# Load development environment variables
load_dotenv('.env.development')

# app = FastAPI()
# app.include_router(auth_router, prefix="/api")

Base.metadata.create_all(bind=engine)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(auth_router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
