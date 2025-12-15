import gradio as gr
import numpy as np
import random
import warnings

try:
    import spaces
except ImportError:
    class _SpacesCompat:
        @staticmethod
        def GPU(*_, **__):
            def decorator(fn):
                return fn

            return decorator

    warnings.warn("spaces GPU decorators unavailable; running without Hugging Face Spaces optimizations.")
    spaces = _SpacesCompat()
    
from diffusers import DiffusionPipeline
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
model_repo_id = "runwayml/stable-diffusion-v1-5"

if torch.cuda.is_available():
    torch_dtype = torch.bfloat16
else:
    torch_dtype = torch.float32

pipe = DiffusionPipeline.from_pretrained(model_repo_id, torch_dtype=torch_dtype)
pipe = pipe.to(device)

MAX_SEED = np.iinfo(np.int32).max
MAX_IMAGE_SIZE = 1024

@spaces.GPU(duration=65)
def infer(
    prompt,
    negative_prompt="",
    seed=42,
    randomize_seed=False,
    width=1024,
    height=1024,
    guidance_scale=4.5,
    num_inference_steps=40,
    progress=gr.Progress(track_tqdm=True),
):
    if randomize_seed:
        seed = random.randint(0, MAX_SEED)

    generator = torch.Generator().manual_seed(seed)

    image = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        guidance_scale=guidance_scale,
        num_inference_steps=num_inference_steps,
        width=width,
        height=height,
        generator=generator,
    ).images[0]

    return image, seed


examples = [
        "A capybara wearing a suit holding a sign that reads Hello World",
]

css = """
#col-container {
    margin: 0 auto;
    max-width: 640px;
}
"""

with gr.Blocks(css=css) as demo:
    with gr.Column(elem_id="col-container"):
        gr.Markdown(" # Model for generating gaming cover pages")
        with gr.Row():
            prompt = gr.Text(
                label="Prompt",
                show_label=False,
                max_lines=1,
                placeholder="Enter your prompt",
                container=False,
            )

            run_button = gr.Button("Run", scale=0, variant="primary")

        result = gr.Image(label="Result", show_label=False)

        with gr.Accordion("Advanced Settings", open=False):
            negative_prompt = gr.Text(
                label="Negative prompt",
                max_lines=1,
                placeholder="Enter a negative prompt",
                visible=False,
            )

            seed = gr.Slider(
                label="Seed",
                minimum=0,
                maximum=MAX_SEED,
                step=1,
                value=0,
            )

            randomize_seed = gr.Checkbox(label="Randomize seed", value=True)

            with gr.Row():
                width = gr.Slider(
                    label="Width",
                    minimum=512,
                    maximum=MAX_IMAGE_SIZE,
                    step=32,
                    value=1024, 
                )

                height = gr.Slider(
                    label="Height",
                    minimum=512,
                    maximum=MAX_IMAGE_SIZE,
                    step=32,
                    value=1024,
                )

            with gr.Row():
                guidance_scale = gr.Slider(
                    label="Guidance scale",
                    minimum=0.0,
                    maximum=7.5,
                    step=0.1,
                    value=4.5,
                )

                num_inference_steps = gr.Slider(
                    label="Number of inference steps",
                    minimum=1,
                    maximum=50,
                    step=1,
                    value=40, 
                )

        gr.Examples(examples=examples, inputs=[prompt], outputs=[result, seed], fn=infer, cache_examples=True)
    gr.on(
        triggers=[run_button.click, prompt.submit],
        fn=infer,
        inputs=[
            prompt,
            negative_prompt,
            seed,
            randomize_seed,
            width,
            height,
            guidance_scale,
            num_inference_steps,
        ],
        outputs=[result, seed],
    )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, inbrowser=True, show_api=False, share=False)