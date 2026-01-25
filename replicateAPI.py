import os
import io
import numpy as np
from replicate.client import Client
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
load_dotenv()


replicate = Client(
    api_token=os.getenv("REPLICATE_API_TOKEN")
)

async def upscale_image(image: str) ->bytes:
	output = replicate.run(
		"tencentarc/gfpgan:0fbacf7afc6c144e5be9767cff80f25aff23e52b0708f17e20f9879b2f21516c",
		input={
			"img": image,
			"scale": 2,
			"version": "v1.4"
		}
	)
	print("Upscaled image:", output)
	return output

async def remove_background(image):
		output = replicate.run(
				"851-labs/background-remover:a029dff38972b5fda4ec5d75d7d1cd25aeff621d2cf4946a41055d7db66b80bc",
				input={
						"image": image,
						"format": "png",
						"reverse": False,
						"threshold": 0,
						"background_type": "transparent"
				}
		)
		return output


