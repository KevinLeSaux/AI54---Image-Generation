from flask import Flask
from flask_cors import CORS

from .api_bp import api_bp

def create_app() -> Flask:
    """Application factory."""
    app = Flask(__name__)
    # Allow frontend dev server to call the API during development.
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.register_blueprint(api_bp, url_prefix="/api")

    return app