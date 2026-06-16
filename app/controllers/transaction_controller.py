from flask import request, jsonify

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