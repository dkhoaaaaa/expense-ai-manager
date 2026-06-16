import time
from flask import request, jsonify

# Import cả 2 mô hình từ file classifier.py
from app.ai.classifier import RuleBasedClassifier, LogisticRegressionClassifier

# Khởi tạo model ở cấp độ Global để lưu vào RAM 1 lần duy nhất
rule_classifier = RuleBasedClassifier()
lr_classifier = LogisticRegressionClassifier(model_path='app/ai/models/lr_expense_model.pkl')

def process_single_transaction(description: str, user_type: str, auto_fallback: bool = True):
    """Hàm helper xử lý logic phân loại cho một giao dịch đơn lẻ."""
    
    # Trích xuất số tiền chung (áp dụng cho mọi tier)
    amount = rule_classifier.extract_amount(description)
    
    # LUỒNG XỬ LÝ CHO NGƯỜI DÙNG PREMIUM (MACHINE LEARNING)
    if user_type == 'PREMIUM':
        probabilities = lr_classifier.predict_proba(description)
        
        # Nếu model ML chưa được train, ép về Rule-based
        if probabilities is None:
            category = rule_classifier.predict_category(description)
            return {
                "original_description": description,
                "amount": amount,
                "category": category,
                "confidence_score": 100.0 if category != "Khác" else 0.0,
                "needs_user_review": category == "Khác",
                "classification_method": "Rule-based (ML Not Trained Fallback)",
            }
            
        # Lấy top dự đoán
        predicted_category = max(probabilities, key=probabilities.get)
        confidence_score = probabilities[predicted_category]
        
        # Sắp xếp xác suất lấy top 3
        sorted_probs = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
        top_3_details = {cat: round(prob * 100, 2) for cat, prob in sorted_probs[:3]}
        
        # 👉 CƠ CHẾ HYBRID FALLBACK (Dự phòng thông minh)
        # Nếu AI không tự tin (< 50%) VÀ tính năng fallback được bật
        if confidence_score < 0.50 and auto_fallback:
            rule_category = rule_classifier.predict_category(description)
            
            # Nếu Rule-based bắt được từ khóa cứng rõ ràng, ưu tiên dùng Rule-based
            if rule_category != "Khác":
                return {
                    "original_description": description,
                    "amount": amount,
                    "category": rule_category,
                    "confidence_score": 100.0,
                    "needs_user_review": False,
                    "classification_method": "Hybrid (ML Low Confidence -> Rule-based Override)",
                    "ml_original_guess": predicted_category # Lưu lại dự đoán gốc của ML để debug
                }

        # Nếu độ tự tin tốt hoặc Rule-based cũng không biết, trả về kết quả ML
        return {
            "original_description": description,
            "amount": amount,
            "category": predicted_category,
            "confidence_score": round(confidence_score * 100, 2),
            "needs_user_review": confidence_score < 0.55,
            "top_predictions": top_3_details,
            "classification_method": "Machine Learning (Logistic Regression)"
        }

    # LUỒNG XỬ LÝ CHO NGƯỜI DÙNG FREE (RULE-BASED)
    else:
        category = rule_classifier.predict_category(description)
        return {
            "original_description": description,
            "amount": amount,
            "category": category,
            "confidence_score": 100.0 if category != "Khác" else 0.0,
            "needs_user_review": category == "Khác",
            "classification_method": "Rule-based Dictionary"
        }

def classify_transactions_advanced():
    """
    API Endpoint nâng cao: Hỗ trợ cả 1 object hoặc 1 list (Batch processing).
    JSON Body dự kiến:
    {
        "transactions": [
            "Mua bó rau 35k",
            "Thanh toán tiền điện 1tr2"
        ],
        "user_type": "PREMIUM",
        "auto_fallback": true
    }
    """
    start_time = time.time()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Không nhận được dữ liệu JSON"}), 400
            
        # Kiểm tra xem user gửi 1 chuỗi (description) hay 1 mảng (transactions)
        transactions = data.get('transactions', [])
        if 'description' in data: # Fallback hỗ trợ API cũ
            transactions.append(data['description'])
            
        if not transactions:
            return jsonify({"status": "error", "message": "Thiếu danh sách 'transactions'"}), 400

        user_type = data.get('user_type', 'USER').upper()
        auto_fallback = data.get('auto_fallback', True)
        
        # Xử lý hàng loạt bằng List Comprehension
        results = [process_single_transaction(text, user_type, auto_fallback) for text in transactions]
        
        # Tính toán thời gian phản hồi
        processing_time_ms = round((time.time() - start_time) * 1000, 2)
        
        return jsonify({
            "status": "success",
            "meta": {
                "total_processed": len(results),
                "processing_time_ms": processing_time_ms,
                "user_type": user_type
            },
            "data": results if len(results) > 1 else results[0] # Nếu gửi 1 thì trả về object, gửi nhiều trả mảng
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Lỗi Server: {str(e)}"}), 500