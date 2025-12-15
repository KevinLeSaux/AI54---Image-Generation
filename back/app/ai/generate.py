import base64
import io
import os
from functools import lru_cache
from pathlib import Path

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS", "1")  # Avoid Windows symlink privilege errors.

import torch

try:
	from accelerate.utils.memory import clear_device_cache  # type: ignore
except ImportError:
	from accelerate.utils import memory as _accelerate_memory

	def _noop_clear_device_cache(*_args, **_kwargs):
		"""Compatibility shim for older accelerate releases."""
		return None

	_accelerate_memory.clear_device_cache = _noop_clear_device_cache

from diffusers import StableDiffusionPipeline
from flask import jsonify, request
from transformers import CLIPTextModel, CLIPTokenizer

from app.utils import payload_validator


MODEL_PATH = Path(__file__).resolve().parent / ".." / "fine_tuned_model.safetensors"
BASE_MODEL_ID = os.environ.get("BASE_MODEL_ID", "runwayml/stable-diffusion-v1-5")


@lru_cache(maxsize=2)
def _load_pipeline(trained: bool) -> StableDiffusionPipeline:
	"""Load the selected Stable Diffusion pipeline once and reuse it."""
	precision = torch.float16 if torch.cuda.is_available() else torch.float32

	if trained:
		if not MODEL_PATH.exists():
			raise FileNotFoundError(f"missing model file: {MODEL_PATH}")
		try:
			pipe = StableDiffusionPipeline.from_pretrained(
				BASE_MODEL_ID,
				torch_dtype=precision,
				safety_checker=None,
			)
			pipe.load_lora_weights(
				MODEL_PATH.parent,
				weight_name=MODEL_PATH.name,
			)
			if hasattr(pipe, "fuse_lora"):
				pipe.fuse_lora()
		except Exception as exc:
			try:
				pipe = StableDiffusionPipeline.from_single_file(
					str(MODEL_PATH.resolve()),
					torch_dtype=precision,
					safety_checker=None,
					text_encoder=_load_base_text_encoder(precision),
					tokenizer=_load_base_tokenizer(),
				)
			except Exception as inner_exc:
				raise RuntimeError(
					"Failed to initialize fine-tuned pipeline; ensure the checkpoint contains either LoRA weights or a full pipeline."
				) from inner_exc
	else:
		pipe = StableDiffusionPipeline.from_pretrained(
			BASE_MODEL_ID,
			torch_dtype=precision,
			safety_checker=None,
		)

	device = "cuda" if torch.cuda.is_available() else "cpu"
	pipe = pipe.to(device)
	pipe.set_progress_bar_config(disable=True)
	return pipe


@lru_cache(maxsize=1)
def _load_base_text_encoder(precision: torch.dtype) -> CLIPTextModel:
	"""Fetch the base text encoder for checkpoints missing this component."""
	text_encoder = CLIPTextModel.from_pretrained(
		BASE_MODEL_ID,
		subfolder="text_encoder",
	)
	return text_encoder.to(dtype=precision)


@lru_cache(maxsize=1)
def _load_base_tokenizer() -> CLIPTokenizer:
	"""Fetch the base tokenizer for checkpoints missing this component."""
	return CLIPTokenizer.from_pretrained(
		BASE_MODEL_ID,
		subfolder="tokenizer",
	)


def route_generate():
	"""
	Generate an image from the requested prompt.
	
	return: JSON response with the base64 encoded PNG.
	"""
	payload = request.get_json(silent=True) or {}

	required_fields = {"prompt": str}

	payload_validator_errors = payload_validator(payload, required_fields)
	if payload_validator_errors:
		return jsonify({"status": "error", "errors": payload_validator_errors}), 400

	trained_flag = bool(payload.get("trained", False)) if "trained" in payload else False

	try:
		pipe = _load_pipeline(trained_flag)
	except Exception as exc:
		return jsonify({"status": "error", "message": str(exc)}), 500

	generator = None
	seed = payload.get("seed")
	if isinstance(seed, int) and seed >= 0:
		generator = torch.Generator(device=pipe.device).manual_seed(seed)

	kwargs = {
		"prompt": payload["prompt"],
		"negative_prompt": payload.get("negative_prompt"),
		"num_inference_steps": payload.get("num_inference_steps", 30),
		"guidance_scale": payload.get("guidance_scale", 7.5),
		"generator": generator,
		"width": payload.get("width"),
		"height": payload.get("height"),
	}

	# Remove keys with None values to avoid diffusers complaints.
	filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}

	if trained_flag and payload.get("lora_scale") is not None:
		try:
			lora_scale = float(payload["lora_scale"])
		except (TypeError, ValueError):
			return jsonify({"status": "error", "message": "invalid lora_scale; expected a number"}), 400
		filtered_kwargs["cross_attention_kwargs"] = {"scale": lora_scale}

	try:
		result = pipe(**filtered_kwargs)
		image = result.images[0]
	except Exception as exc:
		return jsonify({"status": "error", "message": f"generation failed: {exc}"}), 500

	buffer = io.BytesIO()
	image.save(buffer, format="PNG")
	encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")

	return jsonify({"status": "ok", "trained_model": trained_flag, "image": encoded})