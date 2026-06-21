from app import db
from app.models.giaoDichModel import GiaoDich as Transaction
from sqlalchemy import extract
from datetime import datetime


# ➕ CREATE TRANSACTION
def create_transaction(user_id, data):
    t = Transaction(
        idTK=user_id,
        amount=data["amount"],
        type=data["type"],  # income / expense
        category_id=data["category_id"],
        description=data.get("description", ""),
        ngayGiaoDich=datetime.strptime(
            data["ngay_giao_dich"],
            "%Y-%m-%d"
        ).date()
    )

    db.session.add(t)
    db.session.commit()
    return t


# 📥 GET ALL + FILTER
def get_transactions(user_id, filters=None):
    query = Transaction.query.filter_by(idTK=user_id)

    if filters:
        if "day" in filters and filters["day"]:
            query = query.filter(
                extract("day", Transaction.created_at)
                == int(filters["day"])
            )

        if "month" in filters and filters["month"]:
            query = query.filter(
                extract("month", Transaction.created_at)
                == int(filters["month"])
            ) 

        if "type" in filters and filters["type"]:
            query = query.filter_by(type=filters["type"])

        if "category_id" in filters and filters["category_id"]:
            query = query.filter_by(category_id=filters["category_id"])

    return query.all()


# ❌ DELETE
def delete_transaction(user_id, transaction_id):
    t = Transaction.query.filter_by(id=transaction_id, idTK=user_id).first()

    if not t:
        return None

    db.session.delete(t)
    db.session.commit()
    return True

def search_transactions(user_id, keyword):
    return Transaction.query.filter_by(idTK=user_id).filter(
        Transaction.description.like(f"%{keyword}%")
    ).all()

def update_transaction(user_id, transaction_id, data):
    t = Transaction.query.filter_by(id=transaction_id, idTK=user_id).first()

    if not t:
        return None

    t.amount = data.get("amount", t.amount)
    t.type = data.get("type", t.type)
    t.category_id = data.get("category_id", t.category_id)
    t.description = data.get("description", t.description)

    db.session.commit()

    return t