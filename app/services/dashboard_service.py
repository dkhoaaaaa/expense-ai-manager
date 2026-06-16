from app import db
from app.models.transaction import Transaction
from sqlalchemy import func


def get_summary():
    income = db.session.query(func.sum(Transaction.amount))\
        .filter(Transaction.type == "INCOME").scalar() or 0

    expense = db.session.query(func.sum(Transaction.amount))\
        .filter(Transaction.type == "EXPENSE").scalar() or 0

    return {
        "income": income,
        "expense": expense,
        "balance": income - expense
    }


def top_expenses():
    return Transaction.query\
        .filter_by(type="expense")\
        .order_by(Transaction.amount.desc())\
        .limit(5)\
        .all()


def expense_by_category():
    result = db.session.query(
        Transaction.category_id,
        func.sum(Transaction.amount)
    ).filter(Transaction.type == "expense")\
     .group_by(Transaction.category_id).all()

    return [
        {"category_id": r[0], "total": r[1]}
        for r in result
    ]