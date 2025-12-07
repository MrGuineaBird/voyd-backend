import os
import json
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
import aiofiles

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Folders
VIDEO_DIR = "videos"
META_FILE = "metadata.json"

os.makedirs(VIDEO_DIR, exist_ok=True)

# Ensure metadata file exists
if not os.path.exists(META_FILE):
    with open(META_FILE, "w") as f:
        json.dump([], f)

# Load metadata
def load_meta():
    with open(META_FILE, "r") as f:
        return json.load(f)

# Save metadata
def save_meta(data):
    with open(META_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Serve static videos
app.mount("/videos", StaticFiles(directory=VIDEO_DIR), name="videos")


@app.get("/videos/list")
def list_videos():
    return load_meta()


@app.post("/videos/upload")
async def upload_video(
    file: UploadFile = File(...),
    caption: str = Form(""),
):
    ext = file.filename.split(".")[-1]
    vid_id = str(uuid4())
    filename = f"{vid_id}.{ext}"
    filepath = os.path.join(VIDEO_DIR, filename)

    # Save video
    async with aiofiles.open(filepath, "wb") as out:
        content = await file.read()
        await out.write(content)

    # Save metadata
    meta = load_meta()
    entry = {
        "id": vid_id,
        "filename": filename,
        "caption": caption,
    }
    meta.append(entry)
    save_meta(meta)

    return {"success": True, "video": entry}
