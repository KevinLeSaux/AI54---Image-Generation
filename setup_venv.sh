#!/bin/bash
# filepath: setup_venv.sh

# Simple script to setup Python virtual environment with requirements

set -euo pipefail

# Find a Python command (python3, python, or py)
PYTHON_CMD=""
for c in python python3 py; do
    if command -v "$c" >/dev/null 2>&1; then
        PYTHON_CMD="$c"
        break
    fi
done

if [[ -z "$PYTHON_CMD" ]]; then
    echo "Error: Python not found (tried: python3, python, py). Please install Python 3."
    exit 1
fi

echo "Using Python command: $PYTHON_CMD"
"$PYTHON_CMD" --version || true

echo "Creating virtual environment..."
"$PYTHON_CMD" -m venv venv

echo "Activating virtual environment..."
# Windows (Git Bash/Cygwin) vs Linux/Mac
if [[ "$OSTYPE" == msys* || "$OSTYPE" == cygwin* || "$OSTYPE" == win32* ]]; then
    # Git Bash on Windows
    # shellcheck disable=SC1091
    source venv/Scripts/activate
else
    # Linux/Mac
    # shellcheck disable=SC1091
    source venv/bin/activate
fi

echo "Upgrading pip and installing requirements..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "Setup complete! Virtual environment ready."
echo "To activate manually: source venv/bin/activate (Linux/Mac) or source venv/Scripts/activate (Windows)"