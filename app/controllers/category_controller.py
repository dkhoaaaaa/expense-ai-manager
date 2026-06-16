from flask import request, jsonify
from app.services import category_service


def get_categories():
    data = category_service.get_categories()

    return jsonify([
        {"id": c.id, "name": c.name}
        for c in data
    ])


def create_category():
    data = request.json
    c = category_service.create_category(data)

    return jsonify({"id": c.id, "name": c.name})