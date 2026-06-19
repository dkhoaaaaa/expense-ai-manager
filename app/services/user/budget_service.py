from app import db
from app.models.nganSachModel import NganSach as Budget
from app.models.giaoDichModel import GiaoDich as Transaction
from sqlalchemy import func


# 💰 SET BUDGET
def set_budget(data):
    budget = Budget(
        user_id=data["user_id"],
        category_id=data["category_id"],
        month=data["month"],
        year=data["year"],
        limit_amount=data["limit_amount"]
    )

    db.session.add(budget)
    db.session.commit()
    return budget


def get_budget_status(month, year):
    budgets = Budget.query.filter_by(month=month, year=year).all()

    result = []

    for b in budgets:
        spent = db.session.query(func.sum(Transaction.amount))\
            .filter(Transaction.category_id == b.category_id)\
            .filter(Transaction.type == "expense")\
            .scalar() or 0

        # trung bình chi tiêu giả lập (7 ngày gần nhất)
        avg_spent = db.session.query(func.avg(Transaction.amount))\
            .filter(Transaction.type == "expense")\
            .scalar() or 0

        warning = None

        if spent > b.limit_amount:
            warning = "OVER BUDGET"
        elif spent > b.limit_amount * 0.8:
            warning = "NEAR LIMIT"
        elif spent > avg_spent * 1.5:
            warning = "ABOVE AVERAGE SPENDING"

        result.append({
            "category_id": b.category_id,
            "limit": b.limit_amount,
            "spent": spent,
            "avg_spent": avg_spent,
            "warning": warning
        })

    return result