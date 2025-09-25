from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from app.crud.crud_video import create_video, get_videos
from app.schemas.video_schema import VideoCreate, VideoResponse
from auth.routes import get_current_user
from utils.youtube import extract_youtube_id, get_embed_url

router = APIRouter(prefix="/videos", tags=["Videos"])

# ✅ POST /videos/
@router.post("/", response_model=VideoResponse)
def upload_video(video: VideoCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    new_video = create_video(db, video.dict(), uploader_id=current_user.id)
    video_response = VideoResponse.from_orm(new_video)
    return {
        **video_response.dict(),
        "embedUrl": f"https://www.youtube.com/embed/{video_response.youtubeId}"
    }

# ✅ GET /videos/
@router.get("/", response_model=list[VideoResponse])
def fetch_videos(db: Session = Depends(get_db)):
    videos = get_videos(db)
    response_list = []
    for v in videos:
        youtube_id = extract_youtube_id(v.youtube_url)
        video_resp = VideoResponse.from_orm(v)
        response_list.append({
            **video_resp.dict(),
            "youtubeId": youtube_id,
            "embedUrl": get_embed_url(youtube_id)
        })
    return response_list
