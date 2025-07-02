from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from auth.jwt import create_access_token

router = APIRouter()

class LoginInput(BaseModel):
    email: EmailStr
    password: str

@router.post("/auth/login")
def login(data: LoginInput):
    if data.email != "admin@example.com" or data.password != "password123":
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "sub": "1",
        "email": data.email,
        "role": "admin"
    })

    return {"accessToken": token}
