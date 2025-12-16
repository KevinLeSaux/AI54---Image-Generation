from flask import jsonify, request, send_file

from app.utils import payload_validator
import io
def route_trainedModel():
	"""
	Generate image based on prompt.
	
	return: JSON response with image generated.
	"""
 
	print("Received request to generate image from trained model.")
 
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
	import torch
	from diffusers import StableDiffusionPipeline
	from PIL import Image
	import os
	print(torch.cuda.is_available())

	# 1. Load Base Model
	model_id = "runwayml/stable-diffusion-v1-5"
	pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
	pipe = pipe.to("cuda")

	# 2. Load the LoRA weights
	BASE_DIR = os.path.dirname(os.path.abspath(__file__))

	PROJECT_ROOT = os.path.abspath(
		os.path.join(os.path.dirname(__file__), "../../../")
	)

	pipe.load_lora_weights(
		os.path.join(PROJECT_ROOT, "model", "sd-indoor-segmentation-lora"),
		weight_name="pytorch_lora_weights.safetensors"
	)

	# 3. Prompt matches the style used in training
	prompt = "Generate me a cover for an indie zombie video game. There is two zombie on the cover and something that looks like a maze"

	# 4. Generate
	print("Generating LoRA result...")
	image = pipe(prompt, num_inference_steps=30).images[0]

	# 5. Display and Save
	image.save("lora_final_result.png")
	return image