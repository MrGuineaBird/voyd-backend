import os
import uuid
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse, FileResponse
from starlette.status import HTTP_206_PARTIAL_CONTENT
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base
from . import models, crud

Base.metadata.create_all(bind=engine)

UPLOAD_DIR = "videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="VØYD Backend")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    description: str | None = Form(None),
    db: Session = Depends(get_db)
):
    if file.content_type.split("/")[0] != "video":
        raise HTTPException(status_code=400, detail="Only video files allowed")

    ext = os.path.splitext(file.filename)[1] or ".mp4"
    stored_name = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(UPLOAD_DIR, stored_name)

    with open(path, "wb") as out:
        while chunk := await file.read(1024 * 1024):
            out.write(chunk)

    vid = crud.create_video(db, stored_name, file.filename, description)
    return {"id": vid.id, "filename": vid.filename}

@app.get("/videos")
def list_videos(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    vids = crud.get_videos(db, skip, limit)
    return {
        "items": [
            {
                "id": v.id,
                "filename": v.filename,
                "original_name": v.original_name,
                "description": v.description,
                "created_at": v.created_at.isoformat(),
                "likes": v.likes,
                "comments_count": len(v.comments)
            }
            for v in vids
        ]
    }

def iter_file(path, start, length, chunk=1024*1024):
    with open(path, "rb") as f:
        f.seek(start)
        remaining = length
        while remaining > 0:
            data = f.read(min(chunk, remaining))
            if not data:
                break
            remaining -= len(data)
            yield data

@app.get("/video/{video_id}/stream")
def stream(video_id: int, request: Request, db: Session = Depends(get_db)):
    v = crud.get_video(db, video_id)
    if not v:
        raise HTTPException(404)

    path = os.path.join(UPLOAD_DIR, v.filename)
    size = os.path.getsize(path)

    r = request.headers.get("range")
    if r:
        _, rng = r.split("=")
        start, end = rng.split("-")
        start = int(start or 0)
        end = int(end or (size - 1))
        end = min(end, size - 1)

        length = end - start + 1
        headers = {
            "Content-Range": f"bytes {start}-{end}/{size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(length),
            "Content-Type": "video/mp4"
        }
        return StreamingResponse(iter_file(path, start, length), status_code=HTTP_206_PARTIAL_CONTENT, headers=headers)

    return FileResponse(path, media_type="video/mp4")

@app.post("/video/{video_id}/like")
def like(video_id: int, db: Session = Depends(get_db)):
    v = crud.add_like(db, video_id)
    if not v:
        raise HTTPException(404)
    return {"likes": v.likes}

@app.post("/video/{video_id}/comment")
def comment(video_id: int, text: str = Form(...), db: Session = Depends(get_db)):
    c = crud.add_comment(db, video_id, text)
    if not c:
        raise HTTPException(404)
    return {"id": c.id, "text": c.text}

