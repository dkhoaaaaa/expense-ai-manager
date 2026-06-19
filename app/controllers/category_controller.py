from flask import request, jsonify
from app.services.user import category_service


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

def update_category(category_id):
    data = request.json

    c = category_service.update_category(
        category_id,
        data
    )

    if not c:
        return jsonify({"message": "Not found"}), 404

    return jsonify({
        "id": c.id,
        "name": c.name
    })


def delete_category(category_id):
    result = category_service.delete_category(category_id)

    if not result:
        return jsonify({"message": "Not found"}), 404

    return jsonify({
        "message": "Deleted"
    })