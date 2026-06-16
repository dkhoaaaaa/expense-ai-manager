import os
# Import mô hình Logistic Regression từ file classifier.py
from classifier import LogisticRegressionClassifier

def show_terminal_confidence_ui(text: str):
    """
    Hàm in ra bảng phân tích xác suất (Confidence Score) cực đẹp trên Terminal.
    """
    print(f"\n🔍 Đang phân tích mô tả: '{text}'")
    
    # Khởi tạo mô hình (đảm bảo đường dẫn file .pkl chính xác)
    model_path = os.path.join(os.path.dirname(__file__), 'models', 'lr_expense_model.pkl')
    lr_classifier = LogisticRegressionClassifier(model_path=model_path)
    
    # Gọi hàm dự đoán xác suất
    probabilities = lr_classifier.predict_proba(text)
    
    if not probabilities:
        print("❌ Lỗi: Mô hình chưa được huấn luyện. Hãy chạy file train_lr.py trước!")
        return
        
    # Sắp xếp danh mục theo độ tự tin từ cao xuống thấp
    sorted_probs = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
    
    # In Header của bảng
    print("-" * 65)
    print(f"{'DANH MỤC':<15} | {'ĐỘ TỰ TIN':<10} | {'BIỂU ĐỒ TRỰC QUAN'}")
    print("-" * 65)
    
    # In từng dòng kết quả
    for index, (category, prob) in enumerate(sorted_probs):
        percent = prob * 100
        
        # Vẽ biểu đồ ASCII: Mỗi block '█' tương đương 5%. Tổng 20 block = 100%
        bar_length = int(percent / 5)
        bar = '█' * bar_length + '░' * (20 - bar_length)
        
        # Thêm nhãn nhận xét cho kết quả Top 1
        note = ""
        if index == 0:
            if percent >= 80:
                note = " ✅ (Tự tin cao)"
            elif percent >= 50:
                note = " ⚠️ (Tự tin trung bình)"
            else:
                note = " ❌ (Mơ hồ - Cần hỏi lại User)"
                
        # In ra màn hình console
        print(f"{category:<15} | {percent:>6.2f}%   | {bar}{note}")
    print("-" * 65)

# --- THỰC THI TEST ---
if __name__ == "__main__":
    test_cases = [
        "thanh toán tiền điện tháng 11",           # Rất rõ ràng
        "đi ăn lẩu nướng với bạn",                 # Rõ ràng
        "mua vé xem phim xong rớt điện thoại"      # Mập mờ, dễ nhầm lẫn
    ]
    
    for sentence in test_cases:
        show_terminal_confidence_ui(sentence)