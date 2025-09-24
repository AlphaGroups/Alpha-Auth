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
import re
from urllib.parse import urlparse, parse_qs

def get_embed_url(youtube_url: str) -> str:
    # Try to extract video ID
    match = re.search(r"(?:watch\?v=|youtu\.be/)([^&?]+)", youtube_url)
    if not match:
        raise ValueError("Invalid YouTube URL")
    video_id = match.group(1)

    # Extract si parameter if present
    query_params = parse_qs(urlparse(youtube_url).query)
    si_param = query_params.get("si", [None])[0]

    embed_url = f"https://www.youtube.com/embed/{video_id}"
    if si_param:
        embed_url += f"?si={si_param}"
    return embed_url
