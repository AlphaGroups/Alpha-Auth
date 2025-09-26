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
from models import Admin  # <<-- need Admin model

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
    # Teacher / Student: adapt to your app (this assumes User has class_id)
    elif current_user.role == "teacher" or current_user.role == "student":
        user_class_id = getattr(current_user, "class_id", None)
        if not user_class_id:
            return []
        videos = get_videos(db, class_ids=[user_class_id])
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
