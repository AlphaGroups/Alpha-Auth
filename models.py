from sqlalchemy import Column, Integer, String, Enum
import enum
from database import Base

class RoleEnum(str, enum.Enum):
    superadmin = "superadmin"
    admin = "admin"
    teacher = "teacher"
    student = "student"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)              # specify length
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)   # enough for bcrypt
    role = Column(Enum(RoleEnum), default=RoleEnum.student, nullable=False)
