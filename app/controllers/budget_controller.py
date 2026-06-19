from flask import request, jsonify
from app.services.user import budget_service
from app.models.nganSachModel import NganSach as Budget
from app.models.giaoDichModel import GiaoDich as Transaction
from app import db
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity


@jwt_required()
def set_budget():
    user_id = get_jwt_identity()
    data = request.json
    
    # Kiểm tra xem ngân sách cho danh mục/tháng/năm này đã tồn tại chưa
    existing_budget = Budget.query.filter_by(
        user_id=user_id,
        category_id=data["category_id"],
        month=data["month"],
        year=data["year"]
    ).first()
    
    if existing_budget:
        # Cập nhật hạn mức thay vì tạo bản ghi trùng lặp
        existing_budget.limit_amount = data["limit_amount"]
        db.session.commit()
        return jsonify({"status": "success", "message": "Hạn mức ngân sách đã được cập nhật thành công"})
        
    budget = Budget(
        user_id=user_id,
        category_id=data["category_id"],
        month=data["month"],
        year=data["year"],
        limit_amount=data["limit_amount"]
    )

    db.session.add(budget)
    db.session.commit()

    return jsonify({"status": "success", "message": "Thiết lập ngân sách thành công"})


@jwt_required()
def check_budget():
    user_id = get_jwt_identity()
    month_str = request.args.get("month")
    year_str = request.args.get("year")

    # Mặc định lấy tháng năm hiện tại nếu thiếu
    now = datetime.now()
    month = int(month_str) if month_str else now.month
    year = int(year_str) if year_str else now.year

    budgets = Budget.query.filter_by(
        user_id=user_id,
        month=month,
        year=year
    ).all()

    result = []

    for b in budgets:
        # Tính tổng số tiền thực tế đã chi tiêu cho danh mục này trong tháng/năm đó
        spent = Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.category_id == b.category_id,
            Transaction.loai == "CHI",
            db.extract("month", Transaction.ngayGiaoDich) == month,
            db.extract("year", Transaction.ngayGiaoDich) == year
        ).all()

        total_spent = sum(t.amount for t in spent)

        result.append({
            "category_id": b.category_id,
            "limit": float(b.limit_amount),
            "spent": float(total_spent),
            "over": total_spent > b.limit_amount
        })

    return jsonify(result)