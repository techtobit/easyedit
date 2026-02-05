import os
from dotenv import load_dotenv
from replicate.client import Client

load_dotenv()


client = replicate = Client(
    api_token=os.getenv("REPLICATE_API_TOKEN")
)

async def remove_background(image_path):
	uploaded = client.files.create(
    file=open(image_path, "rb"),
	)
	remove_bg = replicate.run(
		"cjwbw/rembg:fb8af171cfa1616ddcf1242c093f9c46bcada5ad4cf6f2fbe8b81b330ec5c003",
		input={
			"image": uploaded.urls["get"],
		}
	)
	return remove_bg.url


async def upscale_image(response):
	if isinstance(response, str):
		input_image = response
	elif hasattr(response, "read"):
		uploaded = client.files.create(file=response)
		input_image = uploaded.urls["get"]
	else:
		raise TypeError("Unsupported input type for upscale_image")

	outputs = replicate.run(
		"tencentarc/gfpgan:ae80bbe1adce7d616b8a96ba88a91d3556838d4f2f4da76327638b8e95ea4694",
		input={
		"img": input_image,
		"scale": 2,
		"version": "v1.3"
		}
	)
	print(".. rep url..", outputs.url)
	return outputs.url


	