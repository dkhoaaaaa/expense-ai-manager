import joblib
import pandas as pd
import numpy as np
import os

def analyze_tfidf_vocabulary(model_path='models/expense_model.pkl'):
    """
    Hàm phân tích xem TF-IDF Vectorizer đã học được những từ khóa nào,
    và từ nào có mức độ quan trọng (IDF) cao nhất.
    """
    print(f"Đang phân tích mô hình: {model_path}\n")
    
    if not os.path.exists(model_path):
        print("❌ Chưa tìm thấy file mô hình. Hãy chạy huấn luyện trước!")
        return

    # 1. Load pipeline đã huấn luyện
    pipeline = joblib.load(model_path)
    
    # 2. Tách TF-IDF và Classifier ra từ Pipeline
    tfidf_step = pipeline.named_steps['tfidf']
    nb_step = pipeline.named_steps['clf']
    
    # Lấy danh sách toàn bộ từ vựng đã học
    feature_names = tfidf_step.get_feature_names_out()
    
    print(f"📊 Tổng số từ vựng (features) AI đã học: {len(feature_names)} từ\n")
    
    # Lấy ra các classes (Danh mục)
    classes = nb_step.classes_
    print(f"🏷️ Các danh mục AI nhận diện: {classes}\n")
    
    # 3. Phân tích xác suất từ khóa (Top keywords) cho từng danh mục
    print("🌟 TOP TỪ KHÓA QUYẾT ĐỊNH CHO TỪNG DANH MỤC:")
    print("-" * 50)
    
    # Naive Bayes lưu xác suất logarit của từng từ trong feature_log_prob_
    for i, category in enumerate(classes):
        # Lấy trọng số của tất cả các từ đối với danh mục này
        top_indices = np.argsort(nb_step.feature_log_prob_[i])[-10:] # Lấy top 10
        top_words = [feature_names[j] for j in top_indices]
        
        # Đảo ngược lại để in từ cao xuống thấp
        top_words.reverse()
        
        print(f"[{category.upper()}]:")
        print(f"   👉 {', '.join(top_words)}\n")

# --- THỰC THI ---
if __name__ == "__main__":
    # Đảm bảo đường dẫn tới file pkl là chính xác
    analyze_tfidf_vocabulary('expense_model.pkl')