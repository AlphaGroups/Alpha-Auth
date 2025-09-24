# import re

# def get_embed_url(youtube_url: str) -> str:
#     video_id = None

#     match = re.search(r"watch\?v=([^&]+)", youtube_url)
#     if match:
#         video_id = match.group(1)

#     match = re.search(r"youtu\.be/([^?]+)", youtube_url)
#     if match:
#         video_id = match.group(1)

#     if not video_id:
#         raise ValueError("Invalid YouTube URL")

#     si_match = re.search(r"[?&]si=([^&]+)", youtube_url)
#     if si_match:
#         return f"https://www.youtube.com/embed/{video_id}?si={si_match.group(1)}"
#     else:
#         return f"https://www.youtube.com/embed/{video_id}"


# utils/youtube.py
import re
from urllib.parse import urlparse, parse_qs

def extract_youtube_id(youtube_url: str) -> str:
    """Extracts YouTube video ID from any valid YouTube URL"""
    match = re.search(r"(?:watch\?v=|youtu\.be/)([^&?]+)", youtube_url)
    if not match:
        raise ValueError("Invalid YouTube URL")
    return match.group(1)

def get_embed_url(video_id: str, si: str = None) -> str:
    """Generates embed URL from video ID"""
    url = f"https://www.youtube.com/embed/{video_id}"
    if si:
        url += f"?si={si}"
    return url
