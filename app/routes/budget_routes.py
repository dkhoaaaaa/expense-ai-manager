from flask import Blueprint
from app.controllers.budget_controller import set_budget, check_budget
budget_bp = Blueprint("budget_bp", __name__)

budget_bp.route("/api/budget", methods=["POST"])(set_budget)
budget_bp.route("/api/budget/check", methods=["GET"])(check_budget)