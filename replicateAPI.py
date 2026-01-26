import os
import requests
import numpy as np
from dotenv import load_dotenv
from replicate.client import Client

load_dotenv()


client = replicate = Client(
    api_token=os.getenv("REPLICATE_API_TOKEN")
)

def remove_background(image_path):
	uploaded = client.files.create(
    file=open(image_path, "rb"),
	)
	remove_bg = replicate.run(
		"cjwbw/rembg:fb8af171cfa1616ddcf1242c093f9c46bcada5ad4cf6f2fbe8b81b330ec5c003",
		input={
			"image": uploaded.urls["get"],
		}
	)
	responses = requests.get(remove_bg.url)
	return responses.content


def upscale_image(image):
	print('image', image)
	with open(image, "rb") as img_file:
		outputs = replicate.run(
		"tencentarc/gfpgan:ae80bbe1adce7d616b8a96ba88a91d3556838d4f2f4da76327638b8e95ea4694",
		input={
		"img": img_file,
		"scale": 2,
		"version": "v1.3"
		}
	)
	print('outputs', outputs)
	return outputs.url