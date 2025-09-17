from pydantic import BaseModel, EmailStr
from typing import Optional

class TeacherCreate(BaseModel):
    full_name: str
    email: EmailStr
    mobile: Optional[str] = None
    password: str
    college_id: int

class TeacherOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    mobile: Optional[str] = None
    college_id: int

    class Config:
        from_attributes = True   # Pydantic v2 replacement for orm_mode
