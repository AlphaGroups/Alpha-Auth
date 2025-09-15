import re

def get_embed_url(youtube_url: str) -> str:
    video_id = None

    match = re.search(r"watch\?v=([^&]+)", youtube_url)
    if match:
        video_id = match.group(1)

    match = re.search(r"youtu\.be/([^?]+)", youtube_url)
    if match:
        video_id = match.group(1)

    if not video_id:
        raise ValueError("Invalid YouTube URL")

    si_match = re.search(r"[?&]si=([^&]+)", youtube_url)
    if si_match:
        return f"https://www.youtube.com/embed/{video_id}?si={si_match.group(1)}"
    else:
        return f"https://www.youtube.com/embed/{video_id}"
