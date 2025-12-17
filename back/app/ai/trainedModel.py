from flask import jsonify, request, send_file
from diffusers import StableDiffusionPipeline
import torch
import io
import os
from typing import Dict
from PIL import Image

model_id = "runwayml/stable-diffusion-v1-5"

pipe = StableDiffusionPipeline.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    device_map="cuda"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "../../../"))

pipe.load_lora_weights(
    os.path.join(PROJECT_ROOT, "model", "sd-indoor-segmentation-lora"),
    weight_name="pytorch_lora_weights.safetensors"
)

print("LoRA model loaded")

# ---- LAZY CACHE ----
example_cache: Dict[str, Image.Image] = {}

def route_trainedModel():
    payload = request.get_json(silent=True) or {}

    prompt = payload.get("prompt")
    negative_prompt = payload.get("negative_prompt", "")
    steps = payload.get("num_inference_steps", 30)
    cfg_scale = payload.get("guidance_scale", 7.5)
    seed = payload.get("seed", -1)
    width = payload.get("width", 512)
    height = payload.get("height", 512)
    lora_scale = payload.get("lora_scale", 1.0)

    if not prompt:
        return jsonify({"error": "Prompt required"}), 400

    # ---- Seed handling ----
    generator = None
    if seed != -1:
        generator = torch.Generator(device="cuda").manual_seed(seed)

    # ---- Cache key ----
    cache_key = (
        f"lora::{prompt}::{negative_prompt}::{steps}::{cfg_scale}::"
        f"{seed}::{width}::{height}::{lora_scale}"
    )

    if cache_key in example_cache:
        print("LoRA image served from cache")
        image = example_cache[cache_key]
    else:
        print("LoRA image generated (cache miss)")

        image = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=steps,
            guidance_scale=cfg_scale,
            width=width,
            height=height,
            generator=generator,
            cross_attention_kwargs={"scale": lora_scale},
        ).images[0]

        example_cache[cache_key] = image

    img_io = io.BytesIO()
    image.save(img_io, "PNG")
    img_io.seek(0)

    return send_file(img_io, mimetype="image/png")


