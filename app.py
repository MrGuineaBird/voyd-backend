from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
from uuid import uuid4
import shutil

app = FastAPI()

# Folder for uploaded videos
VIDEO_DIR = "videos"
os.makedirs(VIDEO_DIR, exist_ok=True)

# Serve videos as static files
app.mount("/videos", StaticFiles(directory=VIDEO_DIR), name="videos")

# Simple in-memory metadata storage
videos_meta = []

@app.get("/")
def home():
    return {"message": "Voyd backend running!"}

@app.get("/videos/list")
def list_videos():
    return videos_meta

@app.post("/videos/upload")
async def upload_video(file: UploadFile = File(...)):
    # Generate a unique filename
    ext = file.filename.split(".")[-1]
    vid_id = str(uuid4())
    filename = f"{vid_id}.{ext}"
    filepath = os.path.join(VIDEO_DIR, filename)

    # Save the uploaded file
    with open(filepath, "wb") as out_file:
        shutil.copyfileobj(file.file, out_file)

    # Add to metadata
    entry = {"id": vid_id, "filename": filename}
    videos_meta.append(entry)

    return JSONResponse({"success": True, "video": entry})
