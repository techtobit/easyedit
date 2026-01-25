import os
import cv2
import uuid
import numpy as np
from face_processing import detect_and_crop
from fastapi import FastAPI, File, UploadFile
from replicate.client import Client
from dotenv import load_dotenv
from validations.validateUpload import validate_upload

load_dotenv()

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
        
        # Read and process the image
        data = await file.read()
        image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        result = detect_and_crop(image, 144, 192)
        if result is None:
            return {"error": "No face detected in the image"}
        
        output_path = f"cropped_{uuid.uuid4().hex}.jpg"
        cv2.imwrite(output_path, result)
        return {"message": "Image processed successfully", "output_path": output_path}
    
    except Exception as e:
        return {"error": str(e)}


# def save_image(image, base_dir="/"):
#     os.makedirs(f"{base_dir}", exist_ok=True)

#     filename = f"{uuid.uuid4().hex}.jpg"
#     filepath = os.path.join(base_dir, filename)

#     cv2.imwrite(filepath, image)
#     return filepath

# replicate = Client(
#     api_token=os.getenv("REPLICATE_API_TOKEN")
# )
# output = replicate.run(
#     "tencentarc/gfpgan:0fbacf7afc6c144e5be9767cff80f25aff23e52b0708f17e20f9879b2f21516c",
#     input={
#         "img": "https://i.ibb.co.com/hB5D2n7/background-5.png",
#         "scale": 2,
#         "version": "v1.4"
#     }
# )

# # To access the file URL:
# print(output.url)
# #=> "http://example.com"

# # To write the file to disk:
# with open("my-image.png", "wb") as file:
#     file.write(output.read())


# output = replicate.run(
#     "851-labs/background-remover:a029dff38972b5fda4ec5d75d7d1cd25aeff621d2cf4946a41055d7db66b80bc",
#     input={
#         "image": "https://i.ibb.co.com/hB5D2n7/background-5.png",
#         "format": "png",
#         "reverse": False,
#         "threshold": 0,
#         "background_type": "red"
#     }
# )

# # To access the file URL:
# print(output.url)
# #=> "http://example.com"

# # To write the file to disk:
# with open("my-image.png", "wb") as file:
#     file.write(output.read())