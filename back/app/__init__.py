from flask import Flask

from .api_bp import api_bp

def create_app() -> Flask:
    """Application factory."""
    app = Flask(__name__)
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.get("/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app
