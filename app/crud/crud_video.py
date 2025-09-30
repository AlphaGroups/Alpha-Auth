# from sqlalchemy.orm import Session
# from models import Video
# from utils.youtube import extract_youtube_id, get_embed_url

# def create_video(db: Session, video_data: dict, uploader_id: int):
#     new_video = Video(
#         title=video_data["title"],
#         description=video_data.get("description"),
#         youtube_url=video_data["youtube_url"],  # full URL
#         category=video_data.get("category"),
#         tags=",".join(video_data.get("tags", [])),
#         difficulty=video_data.get("difficulty"),
#         uploaded_by=uploader_id,
#         class_id=video_data["class_id"]
#     )
#     db.add(new_video)
#     db.commit()
#     db.refresh(new_video)
#     return new_video

# # def get_videos(db: Session):
# #     videos = db.query(Video).all()
# #     return db.query(Video).all()  # ✅ just return ORM list
# #     for v in videos:
# #         youtube_id = extract_youtube_id(v.youtube_url)
# #         result.append({
# #             "id": v.id,
# #             "title": v.title,
# #             "description": v.description,
# #             "youtubeId": youtube_id,
# #             "embedUrl": get_embed_url(youtube_id),
# #             "category": v.category,
# #             "tags": v.tags.split(",") if v.tags else [],
# #             "difficulty": v.difficulty,
# #             "class_id": v.class_id,
# #             "uploaded_by": v.uploaded_by
# #         })
# #     return result

# def get_videos(db: Session, class_ids: list[int] = None):
#     query = db.query(Video)
#     if class_ids:
#         query = query.filter(Video.class_id.in_(class_ids))
#     videos = query.all()

#     result = []
#     for v in videos:
#         youtube_id = extract_youtube_id(v.youtube_url)
#         result.append({
#             "id": v.id,
#             "title": v.title,
#             "description": v.description,
#             "youtubeId": youtube_id,
#             "embedUrl": get_embed_url(youtube_id),
#             "category": v.category,
#             "tags": v.tags.split(",") if v.tags else [],
#             "difficulty": v.difficulty,
#             "class_id": v.class_id,
#             "uploaded_by": v.uploaded_by
#         })
#     return result


# app/crud/crud_video.py
from sqlalchemy.orm import Session
from models import Video

def create_video(db: Session, video_data: dict, uploader_id: int):
    new_video = Video(
        title=video_data["title"],
        description=video_data.get("description"),
        youtube_url=video_data["youtube_url"],
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

def get_videos(db: Session, class_ids: list[int] | None = None):
    """
    Return ORM Video objects. Filter by class_ids if provided.
    The route will handle serialization to the response_model.
    """
    query = db.query(Video)
    if class_ids:
        query = query.filter(Video.class_id.in_(class_ids))
    return query.all()
