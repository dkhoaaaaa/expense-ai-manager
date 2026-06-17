from flask import request, jsonify
from app.services import budget_service
from app.models.budget import Budget
from app.models.transaction import Transaction
from app import db
from datetime import datetime


def set_budget():
    data = request.json

    budget = Budget(
        user_id=data["user_id"],
        category_id=data["category_id"],
        month=data["month"],
        year=data["year"],
        limit_amount=data["limit_amount"]
    )

    db.session.add(budget)
    db.session.commit()

    return jsonify({"message": "Budget created"})


def check_budget():

    budgets = Budget.query.filter_by(
        user_id=user_id,
        month=month,
        year=year
    ).all()

    user_id = request.args.get("user_id")
    month = int(request.args.get("month"))
    year = int(request.args.get("year"))

    user_id = int(request.args.get("user_id"))

    result = []

    for b in budgets:
        spent = Transaction.query.filter_by(
            category_id=b.category_id,
            type="EXPENSE",
            user_id=user_id
        ).all()

        total_spent = sum(t.amount for t in spent)

        result.append({
            "category_id": b.category_id,
            "limit": b.limit_amount,
            "spent": total_spent,
            "over": total_spent > b.limit_amount
        })

    return jsonify(result)