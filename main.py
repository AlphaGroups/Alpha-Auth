import os
from fastapi import FastAPI
from dotenv import load_dotenv
from auth.routes import router as auth_router  # ✅ path relative to root
from database import Base, engine
from models import User
# load_dotenv()

# app = FastAPI()
# app.include_router(auth_router, prefix="/api")

Base.metadata.create_all(bind=engine)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(auth_router, prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # More permissive for deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add a root endpoint to test if the app is running
@app.get("/")
def read_root():
    return {"Hello": "World", "message": "FastAPI is running in Azure!"}

# Add a health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API is running"}
