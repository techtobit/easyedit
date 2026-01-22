import os
from fastapi import UploadFile

UPLOAD_DRI= 'uploads/'
MAX_SIZE = 5*1024*1024  # 5 MB
ALLOWED_TYPES = {'image/png', 'image/jpg', 'image/jpeg', 'image/webp'}


async def validate_upload(file: UploadFile):
	if file.content_type not in ALLOWED_TYPES:
		raise ValueError("Invalid image type. Allowed types are: PNG, JPG, JPEG, WEBP.")
		
	contents = await file.read()
	if len(contents) > MAX_SIZE:
		raise ValueError("File size exceeds the maximum limit of 5 MB.")
	
	file_location = os.path.join(UPLOAD_DRI, file.filename)
	with open(file_location, "wb") as f:
		f.write(contents)
		return file_location