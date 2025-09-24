# # app/routers/video_routes.py
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from datetime import datetime
# from database import get_db
# from models import Video, User, RoleEnum, Student, Teacher, Admin, AdminClassAccess
# from app.schemas.video_schema import VideoCreate, VideoResponse
# from utils.auth import get_current_user
# from typing import List

# router = APIRouter(prefix="/videos", tags=["Videos"])


# # ✅ Upload Video (Superadmin only)
# @router.post("/", response_model=VideoResponse)
# def upload_video(
#     video_data: VideoCreate,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     if current_user.current_role != RoleEnum.superadmin:
#         raise HTTPException(status_code=403, detail="Only Superadmin can upload videos")

#     video = Video(
#         title=video_data.title,
#         description=video_data.description,
#         youtube_id=video_data.youtubeId,
#         category=video_data.category,
#         tags=video_data.tags,
#         difficulty=video_data.difficulty,
#         class_id=video_data.class_id,   # 🎯 assign video to class (1–12)
#         uploaded_by=current_user.id,
#         created_at=datetime.utcnow()
#     )
#     db.add(video)
#     db.commit()
#     db.refresh(video)
#     return video


# # ✅ Get Videos for a Class (role-based access)
# @router.get("/class/{class_id}", response_model=List[VideoResponse])
# def get_videos_for_class(
#     class_id: int,
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user)
# ):
#     role = current_user.current_role

#     # Superadmin can see all
#     if role == RoleEnum.superadmin:
#         return db.query(Video).filter(Video.class_id == class_id).all()

#     # Admins: check class access
#     if role == RoleEnum.admin:
#         has_access = (
#             db.query(AdminClassAccess)
#             .filter(AdminClassAccess.admin_id == current_user.id,
#                     AdminClassAccess.class_id == class_id)
#             .first()
#         )
#         if not has_access:
#             raise HTTPException(status_code=403, detail="Admin has no access to this class")
#         return db.query(Video).filter(Video.class_id == class_id).all()

#     # Teachers: can only see their own class
#     if role == RoleEnum.teacher:
#         teacher = db.query(Teacher).filter(Teacher.id == current_user.id).first()
#         if teacher and teacher.class_id == class_id:
#             return db.query(Video).filter(Video.class_id == class_id).all()
#         raise HTTPException(status_code=403, detail="Teacher cannot access this class")

#     # Students: can only see their own class
#     if role == RoleEnum.student:
#         student = db.query(Student).filter(Student.id == current_user.id).first()
#         if student and student.class_id == class_id:
#             return db.query(Video).filter(Video.class_id == class_id).all()
#         raise HTTPException(status_code=403, detail="Student cannot access this class")

#     raise HTTPException(status_code=403, detail="Invalid role")

# routes/video.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from app.crud.crud_video import create_video, get_videos
from app.schemas.video_schema import VideoCreate, VideoResponse
from auth.routes import get_current_user

router = APIRouter(prefix="/videos", tags=["Videos"])

@router.post("/", response_model=VideoResponse)
def upload_video(video: VideoCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    new_video = create_video(db, video.dict(), uploader_id=current_user.id)
    return {
        **VideoResponse.from_orm(new_video).dict(),
        "embedUrl": f"https://www.youtube.com/embed/{new_video.youtubeId}"
    }

@router.get("/", response_model=list[VideoResponse])
def fetch_videos(db: Session = Depends(get_db)):
    return get_videos(db)
