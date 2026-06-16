import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from classifier import LogisticRegressionClassifier

def train_lr_model(full_dataset_path: str, model_save_path: str):
    print(f"📦 Đang nạp dữ liệu từ: {full_dataset_path}")
    if not os.path.exists(full_dataset_path):
        print("❌ Không tìm thấy file dữ liệu CSV!")
        return

    df = pd.read_csv(full_dataset_path)
    df = df.dropna(subset=['description', 'category'])

    # Chia tập dữ liệu 80% Train, 20% Test
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['category'])
    
    temp_train_path = 'temp_train_lr.csv'
    train_df.to_csv(temp_train_path, index=False)
    
    # KHỞI TẠO VÀ HUẤN LUYỆN
    print("\n🧠 Đang huấn luyện mô hình LOGISTIC REGRESSION...")
    lr_classifier = LogisticRegressionClassifier(model_path=model_save_path)
    success, msg = lr_classifier.train_model(temp_train_path)
    
    if os.path.exists(temp_train_path):
        os.remove(temp_train_path)

    if not success:
        print(f"❌ {msg}")
        return
        
    print("✅ Huấn luyện thành công!\n")

    # ĐÁNH GIÁ MÔ HÌNH (EVALUATION)
    X_test = test_df['description'].tolist()
    y_true = test_df['category'].tolist()
    
    y_pred = [lr_classifier.predict_category(text) for text in X_test]
    
    print("🏆 BÁO CÁO KẾT QUẢ LOGISTIC REGRESSION:")
    print("-" * 60)
    print(f"Độ chính xác tổng thể: {accuracy_score(y_true, y_pred) * 100:.2f}%\n")
    print(classification_report(y_true, y_pred, target_names=sorted(df['category'].unique())))
    print("-" * 60)

    # TEST THỬ XÁC SUẤT (PROBABILITY)
    print("\n🔍 TEST ĐỘ TỰ TIN (CONFIDENCE SCORE) CỦA MÔ HÌNH:")
    test_cases = [
        "ăn cơm sườn nhưng rớt điện thoại phải mua mới", # Câu có vẻ nhập nhằng giữa ăn uống và mua sắm
        "thanh toán tiền điện tháng này"
    ]
    
    for text in test_cases:
        print(f"\nCâu gốc: '{text}'")
        pred = lr_classifier.predict_category(text)
        probs = lr_classifier.predict_proba(text)
        
        print(f"-> Dự đoán chốt: [{pred}]")
        
        # Sắp xếp xác suất từ cao xuống thấp
        sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
        print("-> Phân tích xác suất:")
        for cat, prob in sorted_probs[:3]: # In ra top 3
            print(f"   + {cat}: {prob * 100:.2f}%")


if __name__ == "__main__":
    DATASET_CSV = "large_training_data.csv"
    # Lưu file bằng tên mới để không đè lên Naive Bayes
    MODEL_PKL = os.path.join("models", "lr_expense_model.pkl") 
    
    train_lr_model(full_dataset_path=DATASET_CSV, model_save_path=MODEL_PKL)