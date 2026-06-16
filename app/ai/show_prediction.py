import os
# 👉 Import các class AI từ file classifier.py
from classifier import RuleBasedClassifier, LogisticRegressionClassifier

def display_prediction_results():
    print("🚀 KHỞI ĐỘNG HỆ THỐNG NHẬN DIỆN CHI TIÊU AI...\n")
    
    # 1. Khởi tạo mô hình
    print("⏳ Đang nạp mô hình vào bộ nhớ...")
    rule_classifier = RuleBasedClassifier()
    
    model_path = os.path.join(os.path.dirname(__file__), 'models', 'lr_expense_model.pkl')
    lr_classifier = LogisticRegressionClassifier(model_path=model_path)
    print("✅ Đã nạp mô hình xong!\n")
    
    # 2. Danh sách các câu giao dịch giả định để Test
    test_cases = [
        "ăn cơm tấm sườn bì chả 35k",
        "tiền nhà tháng 11 chuyển khoản 3tr5",
        "mua vé xem phim cgv và bỏng ngô hết 250000",
        "đổ xăng đầy bình 70k",
        "chốt đơn mua đồ linh tinh trên shopee" # Câu khó, thiếu số tiền
    ]
    
    # 3. Vòng lặp hiển thị kết quả chi tiết
    for text in test_cases:
        print("=" * 65)
        print(f"📝 GIAO DỊCH GỐC: '{text}'")
        print("=" * 65)
        
        # --- TRÍCH XUẤT SỐ TIỀN CHUNG ---
        amount = rule_classifier.extract_amount(text)
        print(f"💰 Số tiền trích xuất: {int(amount):,} VNĐ\n")
        
        # --- KẾT QUẢ TỪ RULE-BASED (TÀI KHOẢN USER) ---
        rule_cat = rule_classifier.predict_category(text)
        print("👤 [TÀI KHOẢN CƠ BẢN - Rule-Based]:")
        print(f"   -> Danh mục dự đoán: {rule_cat}")
        print(f"   -> Độ tự tin      : {'100.00%' if rule_cat != 'Khác' else '0.00%'}\n")
        
        # --- KẾT QUẢ TỪ MACHINE LEARNING (TÀI KHOẢN PREMIUM) ---
        print("⭐ [TÀI KHOẢN PREMIUM - Logistic Regression]:")
        probabilities = lr_classifier.predict_proba(text)
        
        if probabilities:
            # Tìm danh mục có xác suất cao nhất
            best_cat = max(probabilities, key=probabilities.get)
            best_score = probabilities[best_cat] * 100
            
            print(f"   -> Danh mục chốt  : {best_cat}")
            print(f"   -> Độ tự tin      : {best_score:.2f}%")
            
            # In phân tích chi tiết (Top 3)
            print("   -> Bảng phân tích chi tiết (Top 3):")
            sorted_probs = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)[:3]
            for cat, prob in sorted_probs:
                print(f"      + {cat:<12}: {prob * 100:>6.2f}%")
                
            # Đưa ra gợi ý kịch bản cho Frontend
            print("\n   [💡 GỢI Ý XỬ LÝ CHO FRONTEND]")
            if best_score < 55:
                print("   ⚠️ Kích hoạt Popup 'Needs Review'. Yêu cầu người dùng xác nhận.")
            else:
                print("   ✅ Tự động lưu (Auto-Fill). Không làm phiền người dùng.")
        else:
            print("   ❌ Lỗi: Mô hình chưa được huấn luyện. File .pkl không tồn tại.")
            
        print("\n")

# --- CHẠY THỰC THI CHƯƠNG TRÌNH ---
if __name__ == "__main__":
    display_prediction_results()