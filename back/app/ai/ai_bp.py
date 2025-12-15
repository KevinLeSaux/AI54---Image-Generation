"""Blueprint entry-point for AI endpoints."""

from flask import Blueprint

from .generate import route_generate

ai_bp = Blueprint("ai", __name__)

ai_bp.add_url_rule("/generate", view_func=route_generate, methods=["POST"])