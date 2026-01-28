import os
import io
import cv2
import time
import tempfile
import numpy as np
from fastapi import Request
from utils.viewLog import logger
from database.data_insert import create_log
from app.face_processing import detect_and_crop
from sqlalchemy.ext.asyncio import AsyncSession
from utils.validateUpload import validate_upload
from database.database import engine, Base, get_db
from fastapi import FastAPI, File, UploadFile, Depends
from app.replicateAPI import remove_background, upscale_image

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def read_root():
    return {"EasyEdit": "Let's enhance your images easily!"}


@app.post("/upload/")
async def create_upload_file(
        request: Request,
        file: UploadFile = File(...),
        input_width: int = File(...),
        input_height: int = File(...),
        db: AsyncSession = Depends(get_db)):
    try:
        # Start timer
        start_time = time.perf_counter()
        
        valid = await validate_upload(file)
        if not valid["status"]:
            return {"error": valid["message"]} 

        if input_width > 0 and input_height >0:
            # Process the image: detect and crop face
            convert_img = await image_convertion(file)
            croped_img = await detect_and_crop(convert_img, input_width, input_height)
            if croped_img is None:
                logger.error(f'No face detected in the image')
                return {"error": "No face detected in the image. Maximize the face size or try another image."}

            tmp_croped_img= await temp_save(croped_img)
            # remove background
            bg_removed = await remove_background(tmp_croped_img)
            logger.info(f"Background removed, URL: {bg_removed}")

            # Upscale image
            upscaled_url = await upscale_image(bg_removed)
            logger.info(f"Image upscaled, URL: {upscaled_url}")
            # Clean up temp files
            os.unlink(tmp_croped_img)

        else:
            bytes_image = await image_convertion(file)
            tmp_croped_img= await temp_save(bytes_image)
            bg_removed = await remove_background(tmp_croped_img)
            logger.info(f"Background removed, URL: {bg_removed}")
            upscaled_url = await upscale_image(bg_removed)
            logger.info(f"Image upscaled, URL: {upscaled_url}")
            os.unlink(tmp_croped_img)

        # Calculate processing time in milliseconds
        total_time = time.perf_counter() - start_time
        total_processing_time = round(total_time , 2)
        
        #Save to db
        await create_log(
            db=db,
            user_id=1,
            processing_time=total_processing_time,
            status="success",
            processed_img=upscaled_url,
        )
        # Return the URL to the frontend
        logger.info(f"Process completed successfully within {total_processing_time:.2f} seconds")
        return {"image_url": upscaled_url}
    
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return {"error": str(e)}


async def image_convertion(file):
    # Read the uploaded file
    contents = await file.read()  
    bytes_to_image = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)
    return bytes_to_image

async def temp_save(image):
    tmp_img= tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    cv2.imwrite(tmp_img.name, image)
    return tmp_img.name


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app", host="0.0.0.0", port=5001, reload=True)


