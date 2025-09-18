from pydantic import BaseModel, EmailStr
from typing import Optional

class CollegeBase(BaseModel):
    name: str


class CollegeCreate(CollegeBase):
    # ✅ Optional embedded admin data
    admin_full_name: str
    admin_email: EmailStr
    admin_mobile: Optional[str] = None
    admin_password: str


class CollegeOut(CollegeBase):
    id: int

    class Config:
        orm_mode = True


class AdminCreate(BaseModel):
    full_name: str
    email: EmailStr
    mobile: Optional[str] = None
    password: str
    college_name: str  # if not exists, create new college


class AdminResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    mobile: Optional[str]
    college_name: str

    class Config:
        orm_mode = True
