#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Root paths
BACKEND_DIR="$ROOT_DIR/back"
FRONTEND_DIR="$ROOT_DIR/front/generative_ai_images"
VENV_DIR="$BACKEND_DIR/venv"

BACKEND_HOST="${BACKEND_HOST:-0.0.0.0}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_HOST="${FRONTEND_HOST:-0.0.0.0}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"
ACTIVATE_SCRIPT=""

# Resolve activation script depending on platform
if [[ -f "$VENV_DIR/bin/activate" ]]; then
    ACTIVATE_SCRIPT="$VENV_DIR/bin/activate"
elif [[ -f "$VENV_DIR/Scripts/activate" ]]; then
    ACTIVATE_SCRIPT="$VENV_DIR/Scripts/activate"
else
    echo "Virtual environment not found in $VENV_DIR. Run back/setup_venv.sh first." >&2
    exit 1
fi

# Launch backend
backend_runner() {
    cd "$BACKEND_DIR"
    # shellcheck disable=SC1090
    source "$ACTIVATE_SCRIPT"
    export BACKEND_HOST BACKEND_PORT
    exec python index.py
}

backend_runner &
BACK_PID=$!
echo "Backend started on ${BACKEND_HOST}:${BACKEND_PORT} (PID: $BACK_PID)"

# Launch frontend (relies on npm)
frontend_runner() {
    cd "$FRONTEND_DIR"
    npm install
    exec npm run dev -- --host "$FRONTEND_HOST" --port "$FRONTEND_PORT"
}

FRONT_PID=""
if command -v npm >/dev/null 2>&1; then
    frontend_runner &
    FRONT_PID=$!
    echo "Frontend started on ${FRONTEND_HOST}:${FRONTEND_PORT} (PID: $FRONT_PID)"
else
    echo "npm not found. Skipping frontend launch." >&2
fi

cleanup() {
    kill "$BACK_PID" 2>/dev/null || true
    if [[ -n "$FRONT_PID" ]]; then
        kill "$FRONT_PID" 2>/dev/null || true
    fi
}

trap cleanup EXIT

echo "Press Ctrl+C to stop both services."

wait "$BACK_PID"
if [[ -n "$FRONT_PID" ]]; then
    wait "$FRONT_PID"
fi
