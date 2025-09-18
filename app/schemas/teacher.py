from pydantic import BaseModel, EmailStr
from typing import Optional

class TeacherCreate(BaseModel):
    full_name: str
    email: EmailStr
    mobile: Optional[str] = None
    password: str
    subject: str      # ✅ new field
    college_id: Optional[int] = None   # ✅ only SuperAdmin uses this

class TeacherOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    mobile: Optional[str] = None
    college_id: int
    subject: str      # ✅ include subject in response

    class Config:
        from_attributes = True   # replacement for orm_mode
