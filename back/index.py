import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    host = os.environ.get("BACKEND_HOST", "0.0.0.0")
    port = int(os.environ.get("BACKEND_PORT", "8000"))
    debug_flag = os.environ.get("FLASK_DEBUG", "1").lower() in {"1", "true", "yes", "on"}
    app.run(host=host, port=port, debug=debug_flag)
