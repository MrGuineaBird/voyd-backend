from sqlalchemy.orm import Session
from . import models

def create_video(db: Session, filename: str, original_name: str, description: str | None):
    v = models.Video(
        filename=filename,
        original_name=original_name,
        description=description
    )
    db.add(v)
    db.commit()
    db.refresh(v)
    return v

def get_videos(db: Session, skip=0, limit=20):
    return db.query(models.Video).order_by(models.Video.created_at.desc()).offset(skip).limit(limit).all()

def get_video(db: Session, video_id: int):
    return db.query(models.Video).filter(models.Video.id == video_id).first()

def add_like(db: Session, video_id: int):
    v = db.query(models.Video).filter(models.Video.id == video_id).first()
    if not v:
        return None
    v.likes += 1
    db.commit()
    db.refresh(v)
    return v

def add_comment(db: Session, video_id: int, text: str):
    v = db.query(models.Video).filter(models.Video.id == video_id).first()
    if not v:
        return None
    c = models.Comment(video_id=video_id, text=text)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c
