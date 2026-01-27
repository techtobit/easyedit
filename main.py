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
from utils.validateUpload import validate_upload
from utils.viewLog import logger
from replicateAPI import remove_background, upscale_image

app = FastAPI()

@app.get("/")
async def read_root():
    return {"EasyEdit": "Let's enhance your images easily!"}

@app.post("/upload/")
async def create_upload_file(
        file: UploadFile = File(...),
        out_width: int = File(...),
        out_height: int = File(...),
    ):
    try:
        valid = await validate_upload(file)
        if not valid["status"]:
            return {"error": valid["message"]}
        
        # Read the uploaded file
        contents = await file.read()
        suffix = os.path.splitext(file.filename)[1].lower() or ".jpg"
        
        # Save the uploaded image
        with open(valid["file_path"], "wb") as save_uploaded_image:
            save_uploaded_image.write(contents)
            logger.info(f"Saved uploaded image to {valid['file_path']}")

        bytes_to_image = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)

        # Process the image: detect and crop face
        croped_img = detect_and_crop(bytes_to_image, out_width, out_height)
        if croped_img is None:
            logger.error(f'No face detected in the image')
            return {"error": "No face detected in the image. Maximize the face size or try another image."}

        # Save cropped image to a temporary file
        tmp_croped_img= tempfile.NamedTemporaryFile(
            suffix=suffix, delete=False
        )
        cv2.imwrite(tmp_croped_img.name, croped_img)
        
        # remove background
        bg_removed = remove_background(tmp_croped_img.name)
        logger.info(f"Background removed, URL: {bg_removed}")

        # Upscale image
        upscaled_url = upscale_image(bg_removed)
        logger.info(f"Image upscaled, URL: {upscaled_url}")
        
        # Clean up temp files
        os.unlink(tmp_croped_img.name)

        # Return the URL to the frontend
        return {"image_url": upscaled_url}
        logger.info("Process completed successfully.")
        # return None
    
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return {"error": str(e)}


