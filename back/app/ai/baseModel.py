from flask import jsonify, request, send_file
from diffusers import StableDiffusionPipeline
import torch
from app.utils import payload_validator
import io

model_id = "runwayml/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16, device_map="cuda")
pipe.enable_attention_slicing()
print("Base model loaded and ready.")


def route_baseModel():
	"""
	Generate image based on prompt.
	
	return: JSON response with image generated.
	"""
 
	print("Received request to generate image from base model.")
 
	payload = request.get_json(silent=True) or {}

	required_fields = {"prompt": str}

	payload_validator_errors = payload_validator(payload, required_fields)
	if payload_validator_errors:
		return jsonify({"status": "error", "errors": payload_validator_errors}), 400

	img = async_generate_image_from_trainedModel()
	
	img_io = io.BytesIO()
	img.save(img_io, "PNG")
	img_io.seek(0)

	return send_file(img_io, mimetype="image/png")

def async_generate_image_from_trainedModel():

	# 2. Prompt for a mask
	prompt = "Generate me a cover for an indie zombie video game. There is two zombie on the cover and something that looks like a maze"

	# 3. Generate
	print("Generating baseline image...")
	image = pipe(prompt).images[0]

	return image