import os
import io
import cv2
import uuid
import base64
import requests
import tempfile
import numpy as np
from face_processing import detect_and_crop
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from validations.validateUpload import validate_upload
from replicateAPI import remove_background, upscale_image

app = FastAPI()


@app.get("/")
async def read_root():
    return {"EasyEdit": "Let's enhance your images easily!"}

@app.post("/upload/")
async def create_upload_file(file: UploadFile = File(...)):
    try:
        valid = await validate_upload(file)
        if not valid["status"]:
            return {"error": valid["message"]}
        
        # Read the uploaded file
        contents = await file.read()
        suffix = os.path.splitext(file.filename)[1].lower() or ".jpg"
        
        image = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)

        # Process the image: detect and crop face
        croped_img = detect_and_crop(image, 144, 192)
        if croped_img is None:
            return {"error": "No face detected in the image. Minimize the face size or try another image."}

        tmp_croped_img= tempfile.NamedTemporaryFile(
            suffix=suffix, delete=False
        )
        cv2.imwrite(tmp_croped_img.name, croped_img)
        
        #remove background
        bg_removed_bytes = remove_background(tmp_croped_img.name)
        
        # Save bg removed to temp file for upscaling
        tmp_bg_removed = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        cv2.imwrite(tmp_bg_removed.name, cv2.imdecode(np.frombuffer(bg_removed_bytes, np.uint8), cv2.IMREAD_UNCHANGED))
        
        #upscale image
        upscaled_url = upscale_image(tmp_bg_removed.name)
        print('upscaled_url', upscaled_url)
        
        # Clean up temp files
        os.unlink(tmp_croped_img.name)
        os.unlink(tmp_bg_removed.name)

        # Return the URL to the frontend
        return {"image_url": upscaled_url}
    
    except Exception as e:
        return {"error": str(e)}


