import os
from dotenv import load_dotenv
from replicate.client import Client

load_dotenv()


client = replicate = Client(
    api_token=os.getenv("REPLICATE_API_TOKEN")
)

		# $0.018 - Test Point - 9
		# "bria/remove-background",
		# $0.01 Test Point - 8
		# "recraft-ai/recraft-remove-background",

		# $0.011 - Test Point - 5
		# "smoretalk/rembg-enhance:c57bc7626c4b5eda6531ffb84657f5672932d0fad49120b94383ec93f7ad7ac6",
		# $0.00052 - Test - 5
		# "851-labs/background-removclearer:a029dff38972b5fda4ec5d75d7d1cd25aeff621d2cf4946a41055d7db66b80bc",
		# $0.0055 - Test Point - 5
		# "cjwbw/rembg:34bd50c3cdcf667a839abdcdde7201d5b39bbebb54aa037da542ee6e670d9786",
		# "cjwbw/rembg:fb8af171cfa1616ddcf1242c093f9c46bcada5ad4cf6f2fbe8b81b330ec5c003",

async def remove_background(image_path):
	uploaded = client.files.create(
    file=open(image_path, "rb"),
	)
	remove_bg = replicate.run(
		# $0.00028 - Test Point - 6
		"lucataco/remove-bg:95fcc2a26d3899cd6c2691c900465aaeff466285a65c14638cc5f36f34befaf1",

		input={
			"image": uploaded.urls["get"],
		}
	)
	print("RBG URL - ", remove_bg.url)
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
	print(".. UPSCAL url..", outputs.url)
	return outputs.url


	