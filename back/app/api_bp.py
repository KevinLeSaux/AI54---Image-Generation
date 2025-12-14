from flask import Blueprint

from .ai.ai_bp import ai_bp

api_bp = Blueprint("api", __name__)

# Group AI-related endpoints under /api/ai
api_bp.register_blueprint(ai_bp, url_prefix="/ai")

