import os
import json
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import aiofiles
from uuid import uuid4

app = FastAPI()

VIDEO_DIR = "videos"
META_FILE = "metadata.json"

os.makedirs(VIDEO_DIR, exist_ok=True)

if not os.path.exists(META_FILE):
    with open(META_FILE, "w") as f:
        json.dump([], f)

def load_meta():
    with open(META_FILE, "r") as f:
        return json.load(f)

def save_meta(data):
    with open(META_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Serve uploaded videos
app.mount("/videos", StaticFiles(directory=VIDEO_DIR), name="videos")

# HTML page
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>VØYD Upload</title>
</head>
<body>
    <h1>Upload a Video</h1>
    <form action="/videos/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="file" required><br><br>
        Caption: <input type="text" name="caption"><br><br>
        <input type="submit" value="Upload">
    </form>
    <h2>Uploaded Videos</h2>
    <ul id="video-list"></ul>
    <script>
        async function loadVideos() {
            const res = await fetch('/videos/list');
            const videos = await res.json();
            const list = document.getElementById('video-list');
            list.innerHTML = '';
            videos.forEach(v => {
                const li = document.createElement('li');
                li.innerHTML = `<video width="320" controls src="/videos/${v.filename}"></video> <br> Caption: ${v.caption}`;
                list.appendChild(li);
            });
        }
        loadVideos();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_PAGE

@app.get("/videos/list")
async def list_videos():
    return load_meta()

@app.post("/videos/upload")
async def upload_video(file: UploadFile = File(...), caption: str = Form("")):
    ext = file.filename.split(".")[-1]
    vid_id = str(uuid4())
    filename = f"{vid_id}.{ext}"
    filepath = os.path.join(VIDEO_DIR, filename)

    async with aiofiles.open(filepath, "wb") as out:
        content = await file.read()
        await out.write(content)

    meta = load_meta()
    entry = {"id": vid_id, "filename": filename, "caption": caption}
    meta.append(entry)
    save_meta(meta)

    return {"success": True, "video": entry}
