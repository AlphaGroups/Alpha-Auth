from pydantic import BaseModel, EmailStr
from typing import Optional


class StudentCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    mobile: str
    roll_number: str
    course: str


class StudentResponse(BaseModel):
    id: int
    full_name: str
    email: str
    mobile: str
    college_id: int
    roll_number: str
    course: str

    class Config:
        from_attributes = True