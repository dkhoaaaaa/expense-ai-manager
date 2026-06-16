from flask import jsonify
from app.services import dashboard_service
from sqlalchemy import func
from app.models.transaction import Transaction
from sqlalchemy import extract


def summary():
    return jsonify(dashboard_service.get_summary())


def top():
    data = dashboard_service.top_expenses()

    return jsonify([
        {"id": t.id, "amount": t.amount, "description": t.description}
        for t in data
    ])


def categories():
    return jsonify(dashboard_service.expense_by_category())

def pie_chart():
    result = db.session.query(
        Transaction.category_id,
        func.sum(Transaction.amount)
    ).filter(Transaction.type == "expense")\
     .group_by(Transaction.category_id).all()

    return jsonify([
        {
            "category_id": r[0],
            "total": r[1]
        }
        for r in result
    ])

def monthly_chart():
    result = db.session.query(
        extract("month", Transaction.created_at),
        func.sum(Transaction.amount)
    ).filter(Transaction.type == "expense")\
     .group_by(extract("month", Transaction.created_at))\
     .order_by(extract("month", Transaction.created_at)).all()

    return jsonify([
        {
            "month": int(r[0]),
            "total": r[1]
        }
        for r in result
    ])