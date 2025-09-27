# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from database import get_db
# from app.crud.crud_video import create_video, get_videos
# from app.schemas.video_schema import VideoCreate, VideoResponse
# from auth.routes import get_current_user
# from utils.youtube import extract_youtube_id, get_embed_url

# router = APIRouter(prefix="/videos", tags=["Videos"])

# # ✅ POST /videos/
# @router.post("/", response_model=VideoResponse)
# def upload_video(video: VideoCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
#     new_video = create_video(db, video.dict(), uploader_id=current_user.id)
#     video_response = VideoResponse.from_orm(new_video)
#     return {
#         **video_response.dict(),
#         "embedUrl": f"https://www.youtube.com/embed/{video_response.youtubeId}"
#     }

# # ✅ GET /videos/
# # @router.get("/", response_model=list[VideoResponse])
# # def fetch_videos(db: Session = Depends(get_db)):
# #     videos = get_videos(db)
# #     response_list = []
# #     for v in videos:
# #         youtube_id = extract_youtube_id(v.youtube_url)
# #         video_resp = VideoResponse.from_orm(v)
# #         response_list.append({
# #             **video_resp.dict(),
# #             "youtubeId": youtube_id,
# #             "embedUrl": get_embed_url(youtube_id)
# #         })
# #     return response_list


# # ✅ GET /videos/
# @router.get("/", response_model=list[VideoResponse])
# def fetch_videos(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
#     # superadmin → see all videos
#     if current_user.role == "superadmin":
#         return get_videos(db)

#     # admin → only videos from allowed class_ids
#     if current_user.role == "admin":
#         class_ids = [access.class_id for access in current_user.class_accesses]
#         if not class_ids:
#             return []  # no access
#         return get_videos(db, class_ids=class_ids)

#     # teacher/student (optional, depends on your logic)
#     if current_user.role == "teacher":
#         return get_videos(db, class_ids=[current_user.class_id])
#     if current_user.role == "student":
#         return get_videos(db, class_ids=[current_user.class_id])

#     return []


# app/routes/video_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from app.crud.crud_video import create_video, get_videos
from app.schemas.video_schema import VideoCreate, VideoResponse
from auth.routes import get_current_user  # returns User instance (for admin/teacher) or Student instance (for students)
from utils.youtube import extract_youtube_id, get_embed_url
from models import Admin, Teacher, Student, Class, Video  # <<-- need all models

router = APIRouter(prefix="/videos", tags=["Videos"])

@router.post("/", response_model=VideoResponse)
def upload_video(video: VideoCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    new_video = create_video(db, video.dict(), uploader_id=current_user.id)
    video_response = VideoResponse.from_orm(new_video)
    # Pydantic v2: prefer model_dump(); v1 uses .dict()
    data = video_response.model_dump()
    data["embedUrl"] = f"https://www.youtube.com/embed/{data.get('youtubeId') or extract_youtube_id(new_video.youtube_url)}"
    return data

@router.get("/", response_model=list[VideoResponse])
def fetch_videos(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Determine the role based on the type of object
    user_role = getattr(current_user, 'role', None)
    if user_role is None:
        # For Student objects, the role should be "student"
        if isinstance(current_user, Student):
            user_role = "student"
        else:
            return []
    
    # Convert enum to string if needed
    if hasattr(user_role, 'value'):
        user_role = user_role.value
    
    # Superadmin -> all videos
    if user_role == "superadmin":
        videos = get_videos(db)
    # Admin -> lookup Admin row & its class_accesses
    elif user_role == "admin":
        admin_record = db.query(Admin).filter(Admin.user_id == current_user.id).first()
        if not admin_record:
            # user has role "admin" but no Admin row: no access
            return []
        class_ids = [access.class_id for access in admin_record.class_accesses]
        if not class_ids:
            return []
        videos = get_videos(db, class_ids=class_ids)
    # Teacher: access videos from all classes in their college
    elif user_role == "teacher":
        # For teachers, we need to query the Teacher table to get their college
        # Then find all classes that have students from the teacher's college
        teacher_record = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
        if not teacher_record:
            return []
        
        # Get all class IDs that have students from the teacher's college
        # This assumes that the classes associated with the teacher's college are those classes
        # that have students from that college
        classes_in_teacher_college = db.query(Student.class_id).filter(
            Student.college_id == teacher_record.college_id
        ).distinct().all()
        
        class_ids = [c.class_id for c in classes_in_teacher_college if c.class_id is not None]
        if not class_ids:
            return []
        
        videos = get_videos(db, class_ids=class_ids)
    # Student: access videos from their assigned class
    elif user_role == "student":
        # For students, current_user is a Student instance from the Student table
        # which has a class_id field
        if hasattr(current_user, 'class_id') and current_user.class_id:
            videos = get_videos(db, class_ids=[current_user.class_id])
        else:
            return []
    else:
        return []

    # Convert ORM Video objects to Pydantic dicts that fully satisfy response_model
    response_list = []
    for v in videos:
        v_resp = VideoResponse.from_orm(v)
        data = v_resp.model_dump()  # use .dict() if on pydantic v1
        # add convenience fields
        youtube_id = extract_youtube_id(v.youtube_url)
        data["youtubeId"] = youtube_id
        data["embedUrl"] = get_embed_url(youtube_id)
        response_list.append(data)

    return response_list
