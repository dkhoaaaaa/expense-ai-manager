from flask import Blueprint, render_template, request, jsonify

demo_bp = Blueprint("demo", __name__)


@demo_bp.route("/")
def home():
    return render_template("demo.html")


@demo_bp.route("/transactions/add", methods=["POST"])
def add_transaction():
    data = request.json
    amount = data.get("amount")
    description = data.get("description")

    # fake AI
    if "ăn" in description.lower():
        category = "Ăn uống"
    elif "xăng" in description.lower():
        category = "Di chuyển"
    else:
        category = "Khác"

    return jsonify({"id": 1, "category": category})
