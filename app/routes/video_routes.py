from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from urllib.parse import urlparse, parse_qs
from database import get_db
from app.schemas.video_schema import VideoCreate, VideoResponse
from models import Video, User
from auth.routes import get_current_user

router = APIRouter(prefix="/videos", tags=["Videos"])

def extract_youtube_id(url_or_id: str) -> str:
    """
    Extract YouTube video ID from a full URL or return if already an ID.
    """
    if "youtube.com" in url_or_id or "youtu.be" in url_or_id:
        parsed_url = urlparse(url_or_id)
        if parsed_url.hostname == "youtu.be":
            return parsed_url.path[1:]
        if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
            if parsed_url.path == "/watch":
                return parse_qs(parsed_url.query)["v"][0]
            if parsed_url.path.startswith("/embed/"):
                return parsed_url.path.split("/")[2]
    # Already an ID
    return url_or_id

@router.post("/", response_model=VideoResponse)
def create_video(
    data: VideoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    youtube_id = extract_youtube_id(data.youtubeId)

    new_video = Video(
        title=data.title,
        description=data.description,
        youtubeId=youtube_id,
        category=data.category,
        tags=",".join(data.tags) if data.tags else None,
        difficulty=data.difficulty,
        uploaded_by=current_user.id,
    )
    db.add(new_video)
    db.commit()
    db.refresh(new_video)

    return VideoResponse.from_orm_with_url(new_video)

# GET endpoint: fetch all videos
@router.get("/", response_model=list[VideoResponse])
def get_videos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    videos = db.query(Video).all()
    result = []

    for video in videos:
        # Convert tags back to list
        tags_list = video.tags.split(",") if video.tags else []
        # Build response object
        video_resp = VideoResponse(
            id=video.id,
            title=video.title,
            description=video.description,
            youtubeId=video.youtubeId,
            category=video.category,
            tags=tags_list,
            difficulty=video.difficulty,
            uploaded_by=video.uploaded_by,
            created_at=video.created_at,
            url=f"https://www.youtube.com/watch?v={video.youtubeId}" if video.youtubeId else ""
        )
        result.append(video_resp)

    return result
