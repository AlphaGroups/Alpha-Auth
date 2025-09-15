
from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Text , Enum
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
    first_name = Column(String(50), nullable=True)   # ✅ added
    last_name = Column(String(50), nullable=True)    # ✅ added
    email = Column(String(100), unique=True, index=True, nullable=False)
    mobile = Column(String(20), nullable=True)       # ✅ added (store as string)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.student, nullable=False)

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)   # ✅ new
    youtubeId = Column(String(20), nullable=False)  # ✅ just store ID
    category = Column(String(100), nullable=True)  # ✅ new
    tags = Column(Text, nullable=True)  # ✅ JSON string (for now)
    difficulty = Column(String(50), nullable=True) # ✅ new
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    uploader = relationship("User", backref="videos")