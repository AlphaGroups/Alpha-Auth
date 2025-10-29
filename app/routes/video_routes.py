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
from models import Admin, Teacher, Student, AdminClassAccess, Video, User  # <<-- need Admin, Teacher, Student, AdminClassAccess, Video, and User models

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
    # Determine the role by checking the type of current_user
    # If current_user is Student, it's a student
    # If current_user is User or has a role attribute, check that
    user_role = getattr(current_user, 'role', None)
    if user_role is None:
        # If there's no role attribute, check if it's a Student object
        if isinstance(current_user, Student):
            user_role = "student"
        elif isinstance(current_user, Teacher):
            user_role = "teacher" 
        elif isinstance(current_user, Admin):
            user_role = "admin"
    
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
    # Teacher: can see videos from their subject and class
    elif user_role == "teacher":
        # Find the teacher record to get their subject and college
        teacher_record = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
        if not teacher_record:
            return []
        
        # For teachers, they should only see videos from their subject in their assigned class
        # Since Teacher model doesn't have class_id directly, we might need to infer from context
        # For now, we'll get all videos from classes that admins in their college have access to,
        # but filter by the teacher's subject (using category field in videos)
        
        # Get all class IDs that admins in this teacher's college have access to
        admin_ids_in_college = db.query(Admin.id).filter(Admin.college_id == teacher_record.college_id).subquery()
        admin_class_accesses = db.query(AdminClassAccess.class_id).filter(
            AdminClassAccess.admin_id.in_(admin_ids_in_college)
        ).all()
        
        admin_class_ids = [access.class_id for access in admin_class_accesses]
        
        # Get videos from admin-accessible classes, filtered by teacher's subject
        # We assume that video 'category' field is used for subject
        if admin_class_ids and teacher_record.subject:
            # Use the existing get_videos function to maintain consistency
            all_videos = get_videos(db, class_ids=admin_class_ids)
            # Filter by teacher's subject
            videos = [v for v in all_videos if v.category == teacher_record.subject]
        else:
            videos = []
    # Student: current_user is actually the Student object itself
    elif user_role == "student":
        try:
            # In this case, current_user IS the student record since get_current_user returns Student
            student_record = current_user
            
            # Students can access all videos from their own class (regardless of subject)
            student_class_id = student_record.class_id
            if student_class_id:
                # Use the existing get_videos function to maintain consistency
                videos = get_videos(db, class_ids=[student_class_id])
            else:
                # If student doesn't have a class_id, they have no access
                return []
        except Exception as e:
            # If there's any error in the student access logic, return empty list
            print(f"Error in student video access: {str(e)}")
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
