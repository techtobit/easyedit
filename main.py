import os
import io
import cv2
import uuid
import numpy as np
import base64
from dotenv import load_dotenv
from fastapi.responses import StreamingResponse
from face_processing import detect_and_crop
from fastapi import FastAPI, File, UploadFile
from validations.validateUpload import validate_upload
from replicateAPI import upscale_image, remove_background
import requests

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
        
        # Save the uploaded file
        contents = await file.read()
        with open(valid["file_path"], "wb") as f:
            f.write(contents)
        await file.seek(0)  # Reset for processing    
        
        
        # Encode image as base64 data URL for raw upload
        image_data_url = f"data:image/jpeg;base64,{base64.b64encode(contents).decode('utf-8')}"
        upscale_images = await upscale_image(image=image_data_url)
        # bg_removed_image =await remove_background(image=upscale_images)
        print("Upscaled image URL:", upscale_images)

        # Read and process the image

        response = requests.get(upscale_images)
        data = response.content
        image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        result = detect_and_crop(image, 144, 192)
        if result is None:
            return {"error": "No face detected in the image"}
        
        output_path = f"cropped_{uuid.uuid4().hex}.jpg"
        cv2.imwrite(output_path, result)

        
        _, buffer = cv2.imencode('.jpg', result)
        
        return StreamingResponse(
            io.BytesIO(buffer.tobytes()),
            media_type="image/jpeg",
            headers={"Content-Disposition": f"attachment; filename={output_path}"}
        )
        # return {"message": "Image processed successfully", "output_path": output_path, "response": response}
    
    except Exception as e:
        return {"error": str(e)}


