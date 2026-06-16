from flask import Blueprint
from app.controllers.transaction_controller import (
    create_transaction,
    get_transactions,
    delete_transaction,
    search_transactions,
    filter_transactions,
    classify_transaction,
    dashboard_summary,
    top_expenses
)

transaction_bp = Blueprint('transaction_bp', __name__)


# CRUD
transaction_bp.route("/api/transactions", methods=["POST"])(create_transaction)
transaction_bp.route("/api/transactions", methods=["GET"])(get_transactions)
transaction_bp.route("/api/transactions/<int:id>", methods=["DELETE"])(delete_transaction)

# SEARCH + FILTER
transaction_bp.route("/api/transactions/search", methods=["GET"])(search_transactions)
transaction_bp.route("/api/transactions/filter", methods=["GET"])(filter_transactions)

# AI CLASSIFY
transaction_bp.route("/api/transactions/classify", methods=["POST"])(classify_transaction)

# DASHBOARD
transaction_bp.route("/api/dashboard", methods=["GET"])(dashboard_summary)

# TOP EXPENSE
transaction_bp.route("/api/transactions/top", methods=["GET"])(top_expenses)

