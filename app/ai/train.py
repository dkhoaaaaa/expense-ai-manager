import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

# 👉 Import class MLClassifier từ file classifier.py của bạn
from classifier import MLClassifier

def train_and_evaluate_model(full_dataset_path: str, model_save_path: str):
    """
    Hàm thực hiện trọn vẹn quy trình: Chia dữ liệu -> Huấn luyện -> Đánh giá
    """
    print(f"📦 Đang nạp dữ liệu từ: {full_dataset_path}")
    if not os.path.exists(full_dataset_path):
        print("❌ Lỗi: Không tìm thấy file dữ liệu. Vui lòng chạy file build_dataset.py trước!")
        return

    # 1. ĐỌC VÀ CHUẨN BỊ DỮ LIỆU
    df = pd.read_csv(full_dataset_path)
    df = df.dropna(subset=['description', 'category'])
    print(f"📊 Tổng số giao dịch: {len(df)} dòng")

    # 2. CHIA TẬP DỮ LIỆU (80% Train, 20% Test)
    # random_state=42 giúp kết quả chia ngẫu nhiên giống hệt nhau ở mọi lần chạy (để dễ debug)
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['category'])
    
    # Lưu tạm tập Train ra file CSV vì hàm train_model() của chúng ta nhận đầu vào là đường dẫn file
    temp_train_path = 'temp_train_data.csv'
    train_df.to_csv(temp_train_path, index=False)
    
    print(f"✂️ Đã chia: {len(train_df)} dòng để Huấn luyện | {len(test_df)} dòng để Kiểm thử\n")

    # 3. KHỞI TẠO VÀ HUẤN LUYỆN MÔ HÌNH
    print("🧠 Đang huấn luyện mô hình Naive Bayes...")
    ml_classifier = MLClassifier(model_path=model_save_path)
    
    success, msg = ml_classifier.train_model(temp_train_path)
    
    # Xóa file train tạm sau khi học xong cho sạch máy
    if os.path.exists(temp_train_path):
        os.remove(temp_train_path)

    if not success:
        print(f"❌ Lỗi huấn luyện: {msg}")
        return
        
    print("✅ Huấn luyện thành công!\n")

    # 4. ĐÁNH GIÁ MÔ HÌNH (EVALUATION)
    print("🎯 ĐANG ĐÁNH GIÁ ĐỘ CHÍNH XÁC TRÊN TẬP KIỂM THỬ (TEST SET)...")
    
    # Lấy dữ liệu test
    X_test = test_df['description'].tolist()
    y_true = test_df['category'].tolist()
    
    # AI tiến hành dự đoán trên các mô tả nó chưa từng được thấy trong lúc học
    # Vì ml_classifier.predict_category nhận từng câu, ta dùng List Comprehension để dự đoán hàng loạt
    y_pred = [ml_classifier.predict_category(text) for text in X_test]
    
    # 5. IN BÁO CÁO KẾT QUẢ (CLASSIFICATION REPORT)
    accuracy = accuracy_score(y_true, y_pred)
    print(f"\n🏆 ĐỘ CHÍNH XÁC TỔNG THỂ (ACCURACY): {accuracy * 100:.2f}%\n")
    
    print("Chi tiết độ chính xác cho từng danh mục:")
    print("-" * 60)
    # Hàm classification_report của sklearn sẽ tự tính toán Precision, Recall và F1-score
    report = classification_report(y_true, y_pred, target_names=sorted(df['category'].unique()))
    print(report)
    print("-" * 60)

# --- THỰC THI ---
if __name__ == "__main__":
    # Đường dẫn file dữ liệu tổng hợp (đã được sinh ra từ build_dataset.py)
    DATASET_CSV = "large_training_data.csv"
    
    # Đường dẫn lưu model sau khi train
    MODEL_PKL = os.path.join("models", "expense_model.pkl")
    
    # Đảm bảo thư mục models/ tồn tại
    os.makedirs(os.path.dirname(MODEL_PKL), exist_ok=True)
    
    # Chạy quy trình
    train_and_evaluate_model(full_dataset_path=DATASET_CSV, model_save_path=MODEL_PKL)