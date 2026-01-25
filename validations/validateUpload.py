import os
from fastapi import UploadFile

UPLOAD_DIR = 'uploads/'
MAX_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_TYPES = {'image/png', 'image/jpeg', 'image/jpg', 'image/webp'}

async def validate_upload(file: UploadFile) -> dict:
    """
    Validates the uploaded file: checks content type and size.
    Returns a dict with status and message/file_path if valid.
    Does not save the file; saving should be handled separately.
    """
    # Check content type
    if file.content_type not in ALLOWED_TYPES:
        return {"status": False, "message": "Invalid image type. Allowed types are: PNG, JPG, JPEG, WEBP."}
    
    # Check file size
    contents = await file.read()
    if len(contents) > MAX_SIZE:
        return {"status": False, "message": "File size exceeds the maximum limit of 5 MB."}
    
    # Reset file pointer for further use
    await file.seek(0)
    
    # If valid, prepare file path (but don't save here)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    
    return {"status": True, "file_path": file_location}