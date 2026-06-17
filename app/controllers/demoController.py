from flask import request, jsonify
from app.services.demoService import create_transaction, predict_expense


def add_transaction():
    data = request.json

    if not data:
        return jsonify({"error": "No data"}), 400

    t = create_transaction(data)

    return jsonify(t)


def predict_transaction():
    result = predict_expense()

    return jsonify({"predicted_expense": result})
