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
    data = request.json or {}
    
    category_id = data.get("category_id")
    month = data.get("month")
    year = data.get("year")
    limit_amount = data.get("limit_amount")
    
    if category_id is None or month is None or year is None or limit_amount is None:
        return jsonify({"status": "error", "message": "Thiếu dữ liệu bắt buộc để thiết lập ngân sách"}), 400
        
    try:
        category_id = int(category_id)
        month = int(month)
        year = int(year)
        limit_amount = float(limit_amount)
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "Dữ liệu ngân sách không hợp lệ"}), 400

    existing_budget = Budget.query.filter_by(
        user_id=user_id,
        category_id=category_id,
        month=month,
        year=year
    ).first()
    
    if existing_budget:
        existing_budget.limit_amount = limit_amount
        db.session.commit()
        return jsonify({"status": "success", "message": "Hạn mức ngân sách đã được cập nhật thành công"})
        
    budget = Budget(
        user_id=user_id,
        category_id=category_id,
        month=month,
        year=year,
        limit_amount=limit_amount
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