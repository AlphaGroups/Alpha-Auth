# from pydantic import BaseModel

# class VideoUpload(BaseModel):
#     title: str
#     url: str


from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from models import Video, User



class VideoBase(BaseModel):
    title: str
    description: Optional[str] = None
    youtubeId: str   # can be ID or URL
    category: str
    tags: List[str] = []
    difficulty: str

    @validator("youtubeId", pre=True)
    def extract_video_id(cls, value):
        if value.startswith("http"):  # if full URL
            parsed_url = urlparse(value)
            query_params = parse_qs(parsed_url.query)
            if "v" in query_params:
                return query_params["v"][0]
        return value  # already an ID

class VideoCreate(VideoBase):
    pass

class VideoResponse(VideoBase):
    id: int
    url: str
    uploaded_by: int
    created_at: datetime

    @classmethod
    def from_orm_with_url(cls, video: "Video"):
        return cls(
            id=video.id,
            title=video.title,
            description=video.description,
            youtubeId=video.youtubeId,
            category=video.category,
            tags=video.tags.split(",") if video.tags else [],
            difficulty=video.difficulty,
            uploaded_by=video.uploaded_by,
            created_at=video.created_at,
            url=f"https://www.youtube.com/watch?v={video.youtubeId}",
        )

    class Config:
        orm_mode = True

