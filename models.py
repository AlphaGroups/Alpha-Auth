from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Text, Enum
import enum
from sqlalchemy.orm import relationship


class RoleEnum(str, enum.Enum):
    superadmin = "superadmin"
    admin = "admin"
    teacher = "teacher"
    student = "student"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    mobile = Column(String(20), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.student, nullable=False)


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    youtubeId = Column(String(20), nullable=False)  # YouTube video ID
    category = Column(String(100), nullable=True)
    tags = Column(Text, nullable=True)
    difficulty = Column(String(50), nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    uploader = relationship("User", backref="videos")


class College(Base):
    __tablename__ = "colleges"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, index=True)

    admins = relationship("Admin", back_populates="college")
    students = relationship("Student", back_populates="college")  # ✅ Add this


class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)  # ✅ Added length
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    college_id = Column(Integer, ForeignKey("colleges.id"))

    college = relationship("College", back_populates="admins")


class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), unique=True, index=True)  # College student ID
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=True)
    birth_year = Column(Integer, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    mobile = Column(String(20), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    college_id = Column(Integer, ForeignKey("colleges.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    college = relationship("College", back_populates="students")
