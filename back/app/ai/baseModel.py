from flask import jsonify, request, send_file
from diffusers import StableDiffusionPipeline
import torch
import io
from typing import Dict
from PIL import Image

# ---- LAZY CACHE ----
example_cache: Dict[str, Image.Image] = {}

def route_baseModel():
    
    
    payload = request.get_json(silent=True) or {}

    prompt = payload.get("prompt")
    steps = payload.get("num_inference_steps", 30)
    cfg_scale = payload.get("guidance_scale", 7.5)
    seed = payload.get("seed", -1)
    width = payload.get("width", 512)
    height = payload.get("height", 512)

    if not prompt:
        return jsonify({"error": "Prompt required"}), 400

    generator = None
    if seed != -1:
        generator = torch.Generator(device="cuda").manual_seed(seed)

    cache_key = f"base::{prompt}::{steps}::{cfg_scale}::{seed}::{width}::{height}"

    if cache_key in example_cache:
        print("Base image served from cache")
        image = example_cache[cache_key]
    else:
                
        model_id = "runwayml/stable-diffusion-v1-5"

        pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            device_map="cuda"
        )
        pipe.enable_attention_slicing()

        print("Base model loaded")
        
        print("Base image generated (cache miss)")
        image = pipe(
            prompt=prompt,
            num_inference_steps=steps,
            guidance_scale=cfg_scale,
            width=width,
            height=height,
            generator=generator,
        ).images[0]
        example_cache[cache_key] = image

    img_io = io.BytesIO()
    image.save(img_io, "PNG")
    img_io.seek(0)

    torch.cuda.empty_cache()

    return send_file(img_io, mimetype="image/png")

