from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Text, Enum, UniqueConstraint
import enum
from sqlalchemy.orm import relationship
from utils.youtube import get_embed_url  # or extract_youtube_id if you renamed it


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
    youtube_url = Column(String(255), nullable=False)  # ✅ full YouTube URL
    category = Column(String(100), nullable=True)
    tags = Column(Text, nullable=True)
    difficulty = Column(String(50), nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)

    uploader = relationship("User", backref="videos")
    class_ = relationship("Class", back_populates="videos")



class College(Base):
    __tablename__ = "colleges"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, index=True)

    admins = relationship("Admin", back_populates="college")
    students = relationship("Student", back_populates="college")  # ✅ Add this


class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    full_name = Column(String(150), nullable=False)  # ✅ Added length
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    college_id = Column(Integer, ForeignKey("colleges.id"))

    college = relationship("College", back_populates="admins")

class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, index=True)
    
    # 🔗 Link to User
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    user = relationship("User", backref="teacher_profile")
    
    full_name = Column(String(150), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    mobile = Column(String(20), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    subject = Column(String(100), nullable=True)

    # 🔗 Link to college
    college_id = Column(Integer, ForeignKey("colleges.id"), nullable=False)
    college = relationship("College", backref="teachers")

    # 🔗 Link to admin who created this teacher
    created_by_admin_id = Column(Integer, ForeignKey("admins.id"), nullable=True)
    created_by_admin = relationship("Admin", backref="created_teachers")

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), unique=True, index=True)  # Unique college ID
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=True)
    birth_year = Column(Integer, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    mobile = Column(String(20), nullable=True)
    hashed_password = Column(String(255), nullable=False)

    # 🔗 Link to college
    college_id = Column(Integer, ForeignKey("colleges.id"), nullable=False)
    college = relationship("College", back_populates="students")

    # 🔗 Link to teacher who created this student
    created_by_teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)
    created_by_teacher = relationship("Teacher", backref="created_students")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # "1", "2", ..., "12"

    # Videos belonging to this class
    videos = relationship("Video", back_populates="class_")

    # Admins who have access to this class
    admins = relationship("AdminClassAccess", back_populates="class_")



class AdminClassAccess(Base):
    __tablename__ = "admin_class_access"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)

    __table_args__ = (UniqueConstraint('admin_id', 'class_id', name='_admin_class_uc'),)

    admin = relationship("Admin", backref="class_accesses")
    class_ = relationship("Class", backref="admin_accesses")