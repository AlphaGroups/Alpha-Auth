from pydantic import BaseModel, EmailStr
from typing import Optional

class CollegeBase(BaseModel):
    name: str

class CollegeCreate(CollegeBase):
    pass

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
    college: str

    class Config:
        orm_mode = True