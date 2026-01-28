import os
import uuid
from fastapi import UploadFile
from utils.viewLog import logger

MAX_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_TYPES = {'image/png', 'image/jpeg', 'image/jpg', 'image/webp'}

async def validate_upload(file: UploadFile) -> dict:
    # Check content type
    if file.content_type not in ALLOWED_TYPES:
        logger.error(f"Invalid file type: {file.content_type}")
        return {"status": False, "message": "Invalid image type. Allowed types are: PNG, JPG, JPEG, WEBP."}
    
    # Check file size
    contents = await file.read()
    if len(contents) > MAX_SIZE:
        logger.error(f"File size exceeds limit: {len(contents)} bytes")
        return {"status": False, "message": "File size exceeds the maximum limit of 5 MB."}
    
    # Reset file pointer for further use
    await file.seek(0)
    
    return {"status": True, "file_path": save_image}