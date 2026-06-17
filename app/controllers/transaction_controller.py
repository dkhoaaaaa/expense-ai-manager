from flask import request, jsonify
from app.services import transaction_service
from datetime import datetime
from app.models.transaction import Transaction
from app import db
from sqlalchemy import extract, func


# 👉 Import Rule-based cho USER và Logistic Regression cho PREMIUM
from app.ai.classifier import RuleBasedClassifier, LogisticRegressionClassifier

# Khởi tạo models ở cấp toàn cục để chỉ load 1 lần khi start server
rule_classifier = RuleBasedClassifier()
lr_classifier = LogisticRegressionClassifier(model_path='app/ai/models/lr_expense_model.pkl')

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
def create_transaction():
    data = request.json
    t = transaction_service.create_transaction(data)

    return jsonify({
        "message": "Created successfully",
        "id": t.id
    })


# 📥 GET
def get_transactions():
    filters = request.args.to_dict()
    data = transaction_service.get_transactions(filters)

    return jsonify([
        {
            "id": t.id,
            "amount": t.amount,
            "type": t.type,
            "category_id": t.category_id,
            "description": t.description
        }
        for t in data
    ])


# ❌ DELETE
def delete_transaction(id):
    transaction_service.delete_transaction(id)
    return jsonify({"message": "Deleted"})

def search_transactions():
    keyword = request.args.get("q")

    data = transaction_service.search_transactions(keyword)

    return jsonify([
        {
            "id": t.id,
            "amount": t.amount,
            "description": t.description
        }
        for t in data
    ])


def filter_transactions():
    """
    GET /api/transactions/filter
    query params:
    - date=YYYY-MM-DD
    - month=MM
    - year=YYYY
    - category_id
    """
    query = Transaction.query

    date = request.args.get("date")
    month = request.args.get("month")
    year = request.args.get("year")
    category_id = request.args.get("category_id")

    if date:
        try:
            d = datetime.strptime(date, "%Y-%m-%d").date()
            query = query.filter(db.func.date(Transaction.created_at) == d)
        except:
            pass

    if month:
       query = query.filter(extract("month", Transaction.created_at) == int(month))
    if year:
       query = query.filter(extract("year", Transaction.created_at) == int(year))
    if category_id:
        query = query.filter(Transaction.category_id == int(category_id))
    data = query.all()

    return jsonify([
        {
            "id": t.id,
            "amount": t.amount,
            "type": t.type,
            "category_id": t.category_id,
            "description": t.description,
            "date": str(t.created_at)
        }
        for t in data
    ])

def dashboard_summary():
    transactions = Transaction.query.all()

    total_income = sum(t.amount for t in transactions if t.type == "INCOME")
    total_expense = sum(t.amount for t in transactions if t.type == "EXPENSE")
    balance = total_income - total_expense

    # group by category
    category_stats = {}

    for t in transactions:
        cat = t.category_id
        category_stats[cat] = category_stats.get(cat, 0) + t.amount

    return jsonify({
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
        "category_stats": category_stats
    })

def top_expenses():
    expenses = Transaction.query.filter_by(type="EXPENSE").order_by(Transaction.amount.desc()).limit(5).all()

    return jsonify([
        {
            "id": t.id,
            "amount": t.amount,
            "description": t.description,
            "category_id": t.category_id
        }
        for t in expenses
    ])

def income_expense_summary():
    income = db.session.query(func.sum(Transaction.amount))\
        .filter(Transaction.type == "INCOME").scalar() or 0

    expense = db.session.query(func.sum(Transaction.amount))\
        .filter(Transaction.type == "EXPENSE").scalar() or 0

    return jsonify({
        "income": income,
        "expense": expense,
        "balance": income - expense
    })

def update_transaction(transaction_id):
    data = request.json

    t = transaction_service.update_transaction(
        transaction_id,
        data
    )

    if not t:
        return jsonify({"message": "Not found"}), 404

    return jsonify({
        "message": "Updated successfully"
    })