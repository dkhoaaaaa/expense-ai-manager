from flask import Blueprint
from app.controllers.dashboard_controller import summary, top, categories
from app.controllers.dashboard_controller import pie_chart, monthly_chart

dashboard_bp = Blueprint("dashboard_bp", __name__)


dashboard_bp.route("/api/dashboard/summary", methods=["GET"])(summary)

dashboard_bp.route("/api/dashboard/top", methods=["GET"])(top)

dashboard_bp.route("/api/dashboard/categories", methods=["GET"])(categories)

dashboard_bp.route("/api/dashboard/pie", methods=["GET"])(pie_chart)

dashboard_bp.route("/api/dashboard/monthly", methods=["GET"])(monthly_chart)