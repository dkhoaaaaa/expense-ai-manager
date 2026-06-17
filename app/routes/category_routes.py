from flask import Blueprint
from app.controllers.category_controller import (
    get_categories,
    create_category
)

category_bp = Blueprint("category_bp", __name__)

category_bp.route("/api/categories", methods=["GET"])(get_categories)
category_bp.route("/api/categories", methods=["POST"])(create_category)