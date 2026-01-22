import os
import replicate
from fastapi import FastAPI, File, UploadFile
from replicate.client import Client
from dotenv import load_dotenv
from validations.validateUpload import validate_upload
load_dotenv()


app = FastAPI()


@app.get("/")
async def read_root():
		return {"EasyEdit": "Let's enhance your images easily!"}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    try:
        file_location = await validate_upload(file)
        return {"filename": file.filename, "location": file_location}
    except ValueError as ve:
        return {"error": str(ve)}

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