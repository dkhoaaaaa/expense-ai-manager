from flask import request, jsonify
from app.services.user import transaction_service
from datetime import datetime
from app.models.giaoDichModel import GiaoDich as Transaction
from app import db
from sqlalchemy import extract, func
from flask_jwt_extended import jwt_required, get_jwt_identity


# 👉 Import Rule-based cho USER và Logistic Regression cho PREMIUM
from app.ai.classifier import RuleBasedClassifier, LogisticRegressionClassifier

# Khởi tạo models ở cấp toàn cục để chỉ load 1 lần khi start server
rule_classifier = RuleBasedClassifier()
lr_classifier = LogisticRegressionClassifier(model_path='app/ai/models/lr_expense_model.pkl')

@jwt_required()
def classify_transaction():
    """
    API Endpoint: /api/transactions/classify
    Method: POST
    JSON Body: {"description": "mua bó rau 35k", "user_type": "PREMIUM"}
    """
    try:
        data = request.get_json()
        
        if not data or 'description' not in data:
            return jsonify({"status": "error", "message": "Thiếu trường 'description' trong request"}), 400
            
        description = data['description']
        user_type = data.get('user_type', 'USER').upper()
        
        # 1. Trích xuất số tiền chung cho cả 2 loại tài khoản
        amount = rule_classifier.extract_amount(description)
        
        # 2. Xử lý phân loại theo hạng tài khoản
        if user_type == 'PREMIUM':
            # Sử dụng tính năng predict_proba của Logistic Regression
            probabilities = lr_classifier.predict_proba(description)
            
            if probabilities is None:
                return jsonify({"status": "error", "message": "Mô hình AI chưa được huấn luyện"}), 500
                
            # Lấy danh mục có xác suất cao nhất
            predicted_category = max(probabilities, key=probabilities.get)
            confidence_score = probabilities[predicted_category]
            
            # Sắp xếp xác suất để trả về Top 3 dự đoán cho Frontend (tùy chọn)
            sorted_probs = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
            top_3_details = {cat: round(prob * 100, 2) for cat, prob in sorted_probs[:3]}
            
            # Đặt ngưỡng (Threshold) để yêu cầu người dùng review
            # Nếu AI tự tin dưới 55%, cờ này sẽ báo True để Frontend hiện Popup xác nhận
            needs_review = confidence_score < 0.55
            
            response_data = {
                "original_description": description,
                "amount": amount,
                "category": predicted_category,
                "confidence_score": round(confidence_score * 100, 2), # Đổi ra phần trăm (vd: 85.50%)
                "needs_user_review": needs_review,
                "top_predictions": top_3_details,
                "classification_method": "Machine Learning (Logistic Regression)"
            }
            
        else:
            # Tài khoản USER (Miễn phí) - Chạy Rule-based
            category = rule_classifier.predict_category(description)
            
            response_data = {
                "original_description": description,
                "amount": amount,
                "category": category,
                "confidence_score": 100.0 if category != "Khác" else 0.0, # Rule-based khớp là 100%, ko khớp là 0%
                "needs_user_review": category == "Khác",
                "top_predictions": None,
                "classification_method": "Rule-based Dictionary"
            }
            
        # 3. Trả về kết quả JSON
        return jsonify({
            "status": "success",
            "data": response_data
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Lỗi Server: {str(e)}"}), 500



# ➕ ADD
@jwt_required()
def create_transaction():
    user_id = get_jwt_identity()
    data = request.json
    t = transaction_service.create_transaction(user_id, data)

    return jsonify({
        "message": "Created successfully",
        "id": t.id
    })


# 📥 GET
@jwt_required()
def get_transactions():
    user_id = get_jwt_identity()
    filters = request.args.to_dict()
    data = transaction_service.get_transactions(user_id, filters)

    return jsonify([
        {
            "id": t.id,
            "amount": float(t.amount),
            "type": t.type,
            "category_id": t.category_id,
            "description": t.description,
            "date": str(t.ngayGiaoDich)
        }
        for t in data
    ])


# ❌ DELETE
@jwt_required()
def delete_transaction(id):
    user_id = get_jwt_identity()
    result = transaction_service.delete_transaction(user_id, id)
    if not result:
        return jsonify({"message": "Not found or unauthorized"}), 404
    return jsonify({"message": "Deleted"})

@jwt_required()
def search_transactions():
    user_id = get_jwt_identity()
    keyword = request.args.get("q")

    data = transaction_service.search_transactions(user_id, keyword)

    return jsonify([
        {
            "id": t.id,
            "amount": float(t.amount),
            "description": t.description,
            "type": t.type,
            "category_id": t.category_id,
            "date": str(t.ngayGiaoDich)
        }
        for t in data
    ])


@jwt_required()
def filter_transactions():
    """
    GET /api/transactions/filter
    query params:
    - date=YYYY-MM-DD
    - month=MM
    - year=YYYY
    - category_id
    """
    user_id = get_jwt_identity()
    query = Transaction.query.filter_by(idTK=user_id)

    date = request.args.get("date")
    month = request.args.get("month")
    year = request.args.get("year")
    category_id = request.args.get("category_id")

    if date:
        try:
            d = datetime.strptime(date, "%Y-%m-%d").date()
            query = query.filter(Transaction.ngayGiaoDich == d)
        except:
            pass

    if month:
       query = query.filter(extract("month", Transaction.ngayGiaoDich) == int(month))
    if year:
       query = query.filter(extract("year", Transaction.ngayGiaoDich) == int(year))
    if category_id:
         query = query.filter(Transaction.category_id == int(category_id))
    data = query.all()

    return jsonify([
        {
            "id": t.id,
            "amount": float(t.amount),
            "type": t.type,
            "category_id": t.category_id,
            "description": t.description,
            "date": str(t.ngayGiaoDich)
        }
        for t in data
    ])

@jwt_required()
def dashboard_summary():
    user_id = get_jwt_identity()
    transactions = Transaction.query.filter_by(idTK=user_id).all()

    total_income = sum(t.amount for t in transactions if t.loai == "THU")
    total_expense = sum(t.amount for t in transactions if t.loai == "CHI")
    balance = total_income - total_expense

    # group by category
    category_stats = {}

    for t in transactions:
        cat = t.category_id
        if cat:
            category_stats[cat] = category_stats.get(cat, 0.0) + float(t.amount)

    return jsonify({
        "total_income": float(total_income),
        "total_expense": float(total_expense),
        "balance": float(balance),
        "category_stats": category_stats
    })

@jwt_required()
def top_expenses():
    user_id = get_jwt_identity()
    expenses = Transaction.query.filter_by(idTK=user_id, loai="CHI").order_by(Transaction.soTien.desc()).limit(5).all()

    return jsonify([
        {
            "id": t.id,
            "amount": float(t.amount),
            "description": t.description,
            "category_id": t.category_id,
            "date": str(t.ngayGiaoDich)
        }
        for t in expenses
    ])

@jwt_required()
def income_expense_summary():
    user_id = get_jwt_identity()
    income = db.session.query(func.sum(Transaction.soTien))\
        .filter(Transaction.idTK == user_id)\
        .filter(Transaction.loai == "THU").scalar() or 0

    expense = db.session.query(func.sum(Transaction.soTien))\
        .filter(Transaction.idTK == user_id)\
        .filter(Transaction.loai == "CHI").scalar() or 0

    return jsonify({
        "income": float(income),
        "expense": float(expense),
        "balance": float(income - expense)
    })

@jwt_required()
def update_transaction(transaction_id):
    user_id = get_jwt_identity()
    data = request.json

    t = transaction_service.update_transaction(
        user_id,
        transaction_id,
        data
    )

    if not t:
        return jsonify({"message": "Not found or unauthorized"}), 404

    return jsonify({
        "message": "Updated successfully"
    })