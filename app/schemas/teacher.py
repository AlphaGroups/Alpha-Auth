from pydantic import BaseModel, EmailStr
from typing import Optional

class TeacherCreate(BaseModel):
    full_name: str
    email: EmailStr
    mobile: Optional[str] = None
    password: str
    college_id: int   # ✅ links teacher to a college
    subject: str      # ✅ new field

class TeacherOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    mobile: Optional[str] = None
    college_id: int
    subject: str      # ✅ include subject in response

    class Config:
        from_attributes = True   # replacement for orm_mode
