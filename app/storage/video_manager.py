import os
import uuid
from fastapi import UploadFile
from pathlib import Path

BASE_VIDEO_DIR = Path("storage/videos")
BASE_VIDEO_DIR.mkdir(parents=True, exist_ok=True)

async def upload_to_storage(video: UploadFile, filename: str) -> str:
    """
    Save uploaded video to local storage and return the URL/path.
    """
    try:
        file_path = BASE_VIDEO_DIR / filename
        with open(file_path, "wb") as buffer:
            while chunk := await video.read(1024 * 1024):  # 1MB chunks
                buffer.write(chunk)
        
        return f"/videos/{filename}"  # URL path (adjust if using static routing)
    except Exception as e:
        raise Exception("Video upload failed: " + str(e))
