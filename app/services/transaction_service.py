from app import db
from app.models.transaction import Transaction


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