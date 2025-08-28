from fastapi import FastAPI
from dotenv import load_dotenv
from auth.routes import router as auth_router
from database import Base, engine
from fastapi.middleware.cors import CORSMiddleware

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
    allow_origins=["http://localhost:3000"],  # frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
