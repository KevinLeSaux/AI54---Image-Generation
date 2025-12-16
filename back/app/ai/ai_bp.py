"""Blueprint entry-point for AI endpoints."""

from flask import Blueprint

from .baseModel import route_baseModel
from .trainedModel import route_trainedModel

ai_bp = Blueprint("ai", __name__)

ai_bp.add_url_rule("/baseModel", view_func=route_baseModel, methods=["POST"])
ai_bp.add_url_rule("/trainedModel", view_func=route_trainedModel, methods=["POST"])

