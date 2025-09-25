from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime
from urllib.parse import urlparse, parse_qs


class VideoBase(BaseModel):
    title: str
    description: Optional[str] = None
    youtube_url: str
    category: Optional[str] = None
    tags: List[str] = []
    difficulty: Optional[str] = None
    class_id: int

    youtubeId: Optional[str] = None
    embedUrl: Optional[str] = None

    # ✅ Extract YouTube ID from URL or accept ID directly
    @field_validator("youtubeId", mode="before")
    def extract_youtube_id(cls, v, info):
        url = info.data.get("youtube_url") if info.data else None
        if url:
            if url.startswith("http"):
                parsed = urlparse(url)
                qs = parse_qs(parsed.query)
                return qs.get("v", [url])[0]  # get ?v= param
        return v or url

    # ✅ Generate embed URL from youtubeId
    @field_validator("embedUrl", mode="after")
    def make_embed_url(cls, v, info):
        youtube_id = info.data.get("youtubeId") if info.data else None
        if youtube_id:
            return f"https://www.youtube.com/embed/{youtube_id}"
        return v

    # ✅ Convert comma-separated string to list for tags
    @field_validator("tags", mode="before")
    def split_tags(cls, v):
        if isinstance(v, str):
            return v.split(",") if v else []
        return v

    model_config = {
        "from_attributes": True
    }


class VideoCreate(VideoBase):
    pass


class VideoResponse(VideoBase):
    id: int
    uploaded_by: int
    created_at: datetime
