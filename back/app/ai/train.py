import json

from flask import Response, jsonify, request, stream_with_context

from app.utils import payload_validator


def route_train():
    """
    Kick off a fine-tuning job using the supplied options.

    param prompt: Base caption that conditions checkpoint validation renders.
    param negative_prompt: Attributes to suppress when generating validation samples.
    param num_inference_steps: Scheduler steps used during validation image generation.
    param guidance_scale: Strength of classifier-free guidance for validation renders.
    param seed: Global random seed applied for repeatable training runs.
    param width: Width of validation previews produced throughout training.
    param height: Height of validation previews produced throughout training.
    param lora_scale: Scaling factor for any LoRA adapters applied during fine-tuning.

    return: JSON payload describing the enqueued training job.
    """

    payload = request.get_json(silent=True) or {}

    # Validate input payload
    required_fields = {
        "prompt": str,
        "negative_prompt": str,
        "num_inference_steps": int,
        "guidance_scale": (int, float),
        "seed": int,
        "width": int,
        "height": int,
        "lora_scale": (int, float),
    }

    payload_validator_errors = payload_validator(payload, required_fields)
    if payload_validator_errors:
        return jsonify({"status": "error", "errors": payload_validator_errors}), 400

    def format_sse(event: str, data: dict) -> str:
        """
        Format a server-sent event (SSE) message.

        param event: The event type.
        param data: The data payload.

        return: Formatted SSE string.
        """
        return f"event: {event}\ndata: {json.dumps(data)}\n\n"

    @stream_with_context
    def event_stream():
        """
        Generator function to stream SSE messages for training progress.
        
        yield: Formatted SSE messages.
        """
        response = {key: payload[key] for key in required_fields}
        response["status"] = "accepted"
        yield format_sse("accepted", response)
        # TODO: perform training here and yield progress updates via format_sse("progress", {...})
        yield format_sse("complete", {"status": "queued"})

    return Response(
        event_stream(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

	

