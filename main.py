from fastapi import FastAPI
from dotenv import load_dotenv
from auth.routes import router as auth_router  # ✅ path relative to root

# load_dotenv()

# app = FastAPI()
# app.include_router(auth_router, prefix="/api")
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
