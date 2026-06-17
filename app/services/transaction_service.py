from app import db
from app.models.transaction import Transaction
from sqlalchemy import extract


# ➕ CREATE TRANSACTION
def create_transaction(data):
    t = Transaction(
        amount=data["amount"],
        type=data["type"],  # income / expense
        category_id=data["category_id"],
        description=data.get("description", "")
    )

    db.session.add(t)
    db.session.commit()
    return t


# 📥 GET ALL + FILTER
def get_transactions(filters=None):
    query = Transaction.query

    if "day" in filters:
        query = query.filter(
            extract("day", Transaction.created_at)
            == int(filters["day"])
        )

    if "month" in filters:
        query = query.filter(
            extract("month", Transaction.created_at)
            == int(filters["month"])
        ) 

    if filters:
        if "type" in filters:
            query = query.filter_by(type=filters["type"])

        if "category_id" in filters:
            query = query.filter_by(category_id=filters["category_id"])

    return query.all()


# ❌ DELETE
def delete_transaction(transaction_id):
    t = Transaction.query.get(transaction_id)

    if not t:
        return None

    db.session.delete(t)
    db.session.commit()
    return True

def search_transactions(keyword):
    return Transaction.query.filter(
        Transaction.description.like(f"%{keyword}%")
    ).all()

def update_transaction(transaction_id, data):
    t = Transaction.query.get(transaction_id)

    if not t:
        return None

    t.amount = data.get("amount", t.amount)
    t.type = data.get("type", t.type)
    t.category_id = data.get("category_id", t.category_id)
    t.description = data.get("description", t.description)

    db.session.commit()

    return t