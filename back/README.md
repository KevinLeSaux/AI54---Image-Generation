# Backend Service

This folder hosts the Flask backend serving the AI image generation endpoints.

## Requirements

- Python 3.10+
- Node.js (only needed if you run the combined launch script)

## Setup

1. Create and activate the virtual environment (one-time):
   ```bash
   cd back
   bash setup_venv.sh
   ```
   > On Windows PowerShell run: `python -m venv venv` then `venv\Scripts\Activate.ps1` and `pip install -r requirements.txt`.

2. Start the server:
   ```bash
   python index.py
   ```
   The process binds to `0.0.0.0:8000` by default. Override with environment variables:
   ```bash
   BACKEND_HOST=127.0.0.1 BACKEND_PORT=9000 python index.py
   ```

## Launch Both Frontend & Backend

From the repo root you can use the helper script:
```bash
BACKEND_PORT=9000 FRONTEND_PORT=5173 ./launch.sh
```
The script activates the virtual environment, starts the Flask app, installs frontend dependencies, and runs Vite. Use `Ctrl+C` to stop both processes.

## API Endpoints

All routes live under the `/api` prefix.

### POST /api/ai/generate

- Purpose: Queue a prompt for image generation.
- Payload: `{ "prompt": "string" }`
- Response: queued job echo (`{ "prompt": "...", "status": "queued" }`).

**cURL**
```bash
curl -X POST http://localhost:8000/api/ai/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"a cat"}'
```

**Invoke-WebRequest (PowerShell)**
```powershell
Invoke-WebRequest http://localhost:8000/api/ai/generate `
  -Method Post `
  -Headers @{"Content-Type"="application/json"} `
  -Body '{"prompt":"a cat"}'
```

### POST /api/ai/train (Server-Sent Events)

- Purpose: Validate parameters and stream training lifecycle events.
- Payload fields (all required):
  - `prompt: str`
  - `negative_prompt: str`
  - `num_inference_steps: int`
  - `guidance_scale: float`
  - `seed: int`
  - `width: int`
  - `height: int`
  - `lora_scale: float`
- Response: SSE stream with `accepted`, subsequent `progress` events (todo), and a final `complete` placeholder.

**cURL (real curl.exe)**
```bash
curl.exe -N http://localhost:8000/api/ai/train \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "prompt":"demo",
    "negative_prompt":"",
    "num_inference_steps":10,
    "guidance_scale":7.5,
    "seed":42,
    "width":512,
    "height":512,
    "lora_scale":1.0
  }'
```

**Invoke-WebRequest** *(buffers the stream; use only when live updates are not required)*
```powershell
Invoke-WebRequest http://localhost:8000/api/ai/train `
  -Method Post `
  -Headers @{"Content-Type"="application/json"; "Accept"="text/event-stream"} `
  -Body '{
    "prompt":"demo",
    "negative_prompt":"",
    "num_inference_steps":10,
    "guidance_scale":7.5,
    "seed":42,
    "width":512,
    "height":512,
    "lora_scale":1.0
  }'
```

> For interactive SSE consumption prefer curl.exe or a frontend client via `EventSource`.

## Development Notes

- New routes live in `app/ai/` and are registered via blueprints.
- Shared validation helpers are located in `app/utils.py`.
- Replace the placeholder TODO sections with calls into your actual generation/training pipelines.
