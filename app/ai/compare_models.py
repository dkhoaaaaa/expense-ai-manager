import os
import time
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# 👉 Import cả 3 mô hình từ file classifier.py của bạn
from classifier import RuleBasedClassifier, MLClassifier, LogisticRegressionClassifier

def benchmark_models(full_dataset_path: str):
    print("⚖️ BẮT ĐẦU QUÁ TRÌNH BENCHMARK SO SÁNH 3 MÔ HÌNH...\n")
    
    if not os.path.exists(full_dataset_path):
        print(f"❌ Lỗi: Không tìm thấy file {full_dataset_path}")
        return

    # 1. ĐỌC VÀ CHIA DỮ LIỆU
    df = pd.read_csv(full_dataset_path)
    df = df.dropna(subset=['description', 'category'])
    
    # Chia 80% Train, 20% Test. Mọi mô hình đều bị kiểm tra trên cùng 1 tập Test này!
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['category'])
    
    temp_train_path = 'temp_benchmark_train.csv'
    train_df.to_csv(temp_train_path, index=False)
    
    X_test = test_df['description'].tolist()
    y_true = test_df['category'].tolist()
    total_test_samples = len(X_test)
    
    print(f"📦 Dữ liệu kiểm thử (Test set): {total_test_samples} giao dịch ẩn (mô hình chưa từng thấy).\n")

    # 2. KHỞI TẠO VÀ HUẤN LUYỆN
    print("⏳ Đang khởi tạo và huấn luyện các mô hình (vui lòng đợi)...")
    
    # Rule-based (Không cần train)
    rule_classifier = RuleBasedClassifier()
    
    # Naive Bayes
    nb_classifier = MLClassifier(model_path='models/benchmark_nb.pkl')
    nb_classifier.train_model(temp_train_path)
    
    # Logistic Regression
    lr_classifier = LogisticRegressionClassifier(model_path='models/benchmark_lr.pkl')
    lr_classifier.train_model(temp_train_path)
    
    # Dọn dẹp file tạm
    if os.path.exists(temp_train_path):
        os.remove(temp_train_path)

    # 3. HÀM TEST ĐÁNH GIÁ TỪNG MÔ HÌNH
    def evaluate(model_name, predict_func):
        # Bắt đầu đo thời gian
        start_time = time.time()
        
        # Dự đoán toàn bộ tập test
        y_pred = [predict_func(text) for text in X_test]
        
        # Kết thúc đo thời gian
        end_time = time.time()
        inference_time = (end_time - start_time) * 1000 # Đổi ra milliseconds
        
        # Tính toán các chỉ số
        acc = accuracy_score(y_true, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted', zero_division=0)
        
        return {
            "Model": model_name,
            "Accuracy": acc * 100,
            "F1-Score": f1 * 100,
            "Time (ms)": inference_time,
            "Speed (ms/req)": inference_time / total_test_samples
        }

    # 4. CHẠY KIỂM THỬ VÀ LƯU KẾT QUẢ
    results = []
    results.append(evaluate("1. Rule-Based (USER)", rule_classifier.predict_category))
    results.append(evaluate("2. Naive Bayes (PREMIUM)", nb_classifier.predict_category))
    results.append(evaluate("3. Logistic Regression (PREMIUM)", lr_classifier.predict_category))

    # 5. IN BẢNG BÁO CÁO SO SÁNH
    print("\n" + "="*80)
    print(f"{'BẢNG SO SÁNH HIỆU NĂNG MÔ HÌNH (BENCHMARK REPORT)':^80}")
    print("="*80)
    
    # Định dạng bảng in ra console
    row_format = "{:<35} | {:<12} | {:<12} | {:<15}"
    print(row_format.format("Tên mô hình", "Độ chính xác", "Điểm F1", "Tốc độ (ms/câu)"))
    print("-" * 80)
    
    for r in results:
        acc_str = f"{r['Accuracy']:.2f}%"
        f1_str = f"{r['F1-Score']:.2f}%"
        speed_str = f"{r['Speed (ms/req)']:.3f} ms"
        print(row_format.format(r['Model'], acc_str, f1_str, speed_str))
    
    print("="*80)

# --- THỰC THI ---
if __name__ == "__main__":
    DATASET_CSV = "large_training_data.csv"
    benchmark_models(DATASET_CSV)