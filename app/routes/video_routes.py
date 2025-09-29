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
from auth.routes import get_current_user  # returns User instance
from utils.youtube import extract_youtube_id, get_embed_url
from models import Admin, Teacher, Student, AdminClassAccess  # <<-- need Admin, Teacher, Student, and AdminClassAccess models

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
    # Superadmin -> all videos
    if current_user.role == "superadmin":
        videos = get_videos(db)
    # Admin -> lookup Admin row & its class_accesses
    elif current_user.role == "admin":
        admin_record = db.query(Admin).filter(Admin.user_id == current_user.id).first()
        if not admin_record:
            # user has role "admin" but no Admin row: no access
            return []
        class_ids = [access.class_id for access in admin_record.class_accesses]
        if not class_ids:
            return []
        videos = get_videos(db, class_ids=class_ids)
    # Teacher: can see videos from classes that admins in their college have access to
    elif current_user.role == "teacher":
        # Find the teacher record to get their college
        teacher_record = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
        if not teacher_record:
            return []
        
        # Get all class IDs that admins in this teacher's college have access to
        admin_ids_in_college = db.query(Admin.id).filter(Admin.college_id == teacher_record.college_id).subquery()
        admin_class_accesses = db.query(AdminClassAccess.class_id).filter(
            AdminClassAccess.admin_id.in_(admin_ids_in_college)
        ).all()
        
        admin_class_ids = [access.class_id for access in admin_class_accesses]
        
        # Teachers might also have access to specific classes, but this is handled by admin access
        all_class_ids = list(set(admin_class_ids))
        
        videos = get_videos(db, class_ids=all_class_ids) if all_class_ids else []
    # Student: for students, we need to determine their record somehow
    # Since there's no direct user_id in Student model linking to User, let's assume
    # that students might have their class set in User model (though this needs to be verified in auth implementation)
    elif current_user.role == "student":
        # For students, we'll implement access based on admin access in their college
        # First, we need to find which college the student belongs to
        
        # The Student model has its own email, student_id, etc., and is not directly linked to User
        # This seems to be a design issue in the schema. 
        # The proper solution would be to link Student to User, but since that's not in the current schema,
        # we'll have to handle it differently.
        
        # If the auth system authenticates using the User table and the User.role is 'student',
        # then we need a way to link the User to the Student record.
        # Let's assume that for students, we need to have a different approach.
        # Since the Student model is not directly linked to User, we'll have to assume that
        # when a student logs in, they do so through a specific mechanism.
        
        # If the application is designed such that students are linked to users in another way,
        # we might need to add the user_id field to the Student model.
        # For now, I'll assume that students can access based on the admin access in their college,
        # and that there should be a mechanism to identify which college a student belongs to.
        
        # Let's query for the student by email (current_user.email) to find their record
        student_record = db.query(Student).filter(Student.email == current_user.email).first()
        if not student_record:
            # If we can't find the student by email, they might not have access
            # OR the system might be designed differently (user_id linking)
            # This suggests that we might need to add user_id to Student model
            return []
        
        college_id = student_record.college_id
        
        # Get all class IDs that admins in this student's college have access to
        admin_ids_in_college = db.query(Admin.id).filter(Admin.college_id == college_id).subquery()
        admin_class_accesses = db.query(AdminClassAccess.class_id).filter(
            AdminClassAccess.admin_id.in_(admin_ids_in_college)
        ).all()
        
        admin_class_ids = [access.class_id for access in admin_class_accesses]
        
        # Student also has access to their own class
        student_class_id = student_record.class_id
        if student_class_id:
            admin_class_ids.append(student_class_id)
        
        # Remove duplicates while preserving order
        all_class_ids = list(dict.fromkeys(admin_class_ids))
        
        videos = get_videos(db, class_ids=all_class_ids) if all_class_ids else []
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
