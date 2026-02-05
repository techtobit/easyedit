import os
import io
import cv2
import time
import base64
import tempfile
import numpy as np
from PIL import Image
from utils.viewLog import logger
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from database.data_insert import create_log
from fastapi.templating import Jinja2Templates
from app.face_processing import detect_and_crop
from sqlalchemy.ext.asyncio import AsyncSession
from utils.validateUpload import validate_upload
from database.database import engine, Base, get_db
from app.replicateAPI import remove_background, upscale_image
from fastapi import FastAPI, Form, File, UploadFile, Request, Depends

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="template")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={}
    )

@app.post("/upload/")
async def create_upload_file(
        request: Request,
        file: UploadFile = File(...),
        input_width: int = Form(0),
        input_height: int = Form(0),
        bgtype: str = Form('original'),
        db: AsyncSession = Depends(get_db)
    ):
    try:
        start_time = time.perf_counter()

        # 1. Validate
        valid = await validate_upload(file)
        if not valid["status"]:
            return {"error": valid["message"]}

        # 2. Convert file once
        img_to_btyes = await image_convertion(file)

        result_img = None  # this will always be fed to upscaler
        tmp_files = []

        is_custom_size = input_width > 0 and input_height > 0
        is_original_size = not is_custom_size

        # --------------------------------------------------
        # CASE 1: custom size + custom color
        # mediapipe → removebg → upscaler
        # --------------------------------------------------
        if is_custom_size and bgtype == "transparent":
            cropped_img = await detect_and_crop(img_to_btyes, input_width, input_height)
            if cropped_img is None:
                return {"error": "No face detected"}
            tmp = await temp_save(cropped_img)
            tmp_files.append(tmp)

            bg_removed = await remove_background(tmp)
            result_img = bg_removed
            # working

        # --------------------------------------------------
        # CASE 2: original size + original color
        # upscaler only
        # --------------------------------------------------
        elif is_original_size and bgtype == "original":
            result_img = await cv_to_imagefile(img_to_btyes)
            # working 


        # --------------------------------------------------
        # CASE 3: custom size + original color
        # mediapipe → upscaler
        # --------------------------------------------------
        elif is_custom_size and bgtype == "original":
            cropped_img = await detect_and_crop(img_to_btyes, input_width, input_height)
            if cropped_img is None:
                return {"error": "No face detected"}
            result_img = await cv_to_imagefile(cropped_img)
            # working

        # --------------------------------------------------
        # CASE 4: original size + transparent
        # upscaler → removebg
        # --------------------------------------------------
        elif is_original_size and bgtype == "transparent":
            tmp = await temp_save(img_to_btyes)
            tmp_files.append(tmp)
            bg_removed = await remove_background(tmp)
            result_img = bg_removed
            # working

        # --------------------------------------------------
        # FINAL: always upscale
        # --------------------------------------------------
        upscaled_url = await upscale_image(result_img)

        # Cleanup
        for file in tmp_files:
            if os.path.exists(file):
                os.unlink(file)

        total_time = round(time.perf_counter() - start_time, 2)

        await create_log(
            db=db,
            user_id=1,
            processing_time=total_time,
            status="success",
            processed_img=upscaled_url,
        )

        return {
            "image_url": upscaled_url,
            "processing_time": total_time
        }

    except Exception as e:
        logger.error(str(e))
        return {"error": str(e)}

async def image_convertion(file):
    # Read the uploaded file
    contents = await file.read()  
    bytes_to_image = cv2.imdecode(np.frombuffer(contents, np.uint8), cv2.IMREAD_COLOR)
    return bytes_to_image

async def cv_to_imagefile(img_cv):
    success, buffer = cv2.imencode('.png', img_cv)
    if not success:
        raise ValueError("Failed to encode image")
    file_obj = io.BytesIO(buffer.tobytes())
    file_obj.name = "image.png"
    return file_obj


async def temp_save(image):
    tmp_img= tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    cv2.imwrite(tmp_img.name, image)
    return tmp_img.name

