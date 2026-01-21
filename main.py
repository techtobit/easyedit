from fastapi import FastAPI
import replicate
import os
from dotenv import load_dotenv
load_dotenv()
from replicate.client import Client
app = FastAPI()

@app.get("/")
async def read_root():
		return {"Hello": "World"}


# def enhance_image(image_url: str):
# replicate.Client(api_token=os.getenv("REPLICATE_API_TOKEN"))


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


output = replicate.run(
    "851-labs/background-remover:a029dff38972b5fda4ec5d75d7d1cd25aeff621d2cf4946a41055d7db66b80bc",
    input={
        "image": "https://i.ibb.co.com/hB5D2n7/background-5.png",
        "format": "png",
        "reverse": False,
        "threshold": 0,
        "background_type": "rgba"
    }
)

# To access the file URL:
print(output.url)
#=> "http://example.com"

# To write the file to disk:
with open("my-image.png", "wb") as file:
    file.write(output.read())