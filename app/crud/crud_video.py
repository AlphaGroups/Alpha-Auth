# crud/video.py
from sqlalchemy.orm import Session
from models import Video
from utils.youtube import extract_youtube_id, get_embed_url

def create_video(db: Session, video_data: dict, uploader_id: int):
    video_id = extract_youtube_id(video_data["youtubeUrl"])
    new_video = Video(
        title=video_data["title"],
        description=video_data.get("description"),
        youtubeId=video_id,
        category=video_data.get("category"),
        tags=",".join(video_data.get("tags", [])),
        difficulty=video_data.get("difficulty"),
        uploaded_by=uploader_id,
        class_id=video_data["class_id"]
    )
    db.add(new_video)
    db.commit()
    db.refresh(new_video)
    return new_video

def get_videos(db: Session):
    videos = db.query(Video).all()
    result = []
    for v in videos:
        result.append({
            "id": v.id,
            "title": v.title,
            "description": v.description,
            "youtubeId": v.youtubeId,
            "embedUrl": get_embed_url(v.youtubeId),
            "category": v.category,
            "tags": v.tags.split(",") if v.tags else [],
            "difficulty": v.difficulty,
            "class_id": v.class_id,
            "uploaded_by": v.uploaded_by
        })
    return result
