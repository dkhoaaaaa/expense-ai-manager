import re
import os
import unicodedata
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib
from .text_utils import clean_vietnamese_text
from sklearn.linear_model import LogisticRegression
# --- HÀM CHUẨN HÓA VĂN BẢN TIẾNG VIỆT ---
def normalize_vietnamese_text(text: str) -> str:
    """
    Chuẩn hóa văn bản đầu vào:
    1. Đưa về chuẩn Unicode NFC (tránh lỗi font chữ tổ hợp/dựng sẵn trong tiếng Việt).
    2. Chuyển thành chữ thường.
    3. Xóa khoảng trắng thừa.
    """
    if not isinstance(text, str):
        return ""
    
    # 1. Chuẩn hóa Unicode
    text = unicodedata.normalize('NFC', text)
    
    # 2. Chuyển về chữ thường
    text = text.lower()
    
    # 3. Xóa khoảng trắng thừa (nhiều dấu cách liên tiếp chuyển thành 1 dấu cách)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


# --- 1. RULE-BASED CLASSIFIER ---
class RuleBasedClassifier:
    def __init__(self):
        # Từ điển ánh xạ: Danh mục -> Danh sách từ khóa
        self.category_mapping = {
            "Ăn uống": [
                "cơm", "phở", "bún", "trà sữa", "cafe", "cà phê", "nhậu", 
                "ăn sáng", "siêu thị", "đồ ăn", "nước", "bánh", "pizza"
            ],
            "Đi lại": [
                "xăng", "grab", "be", "gojek", "taxi", "gửi xe", "vé xe", 
                "rửa xe", "bảo dưỡng", "thay nhớt", "xe buýt"
            ],
            "Hóa đơn": [
                "điện", "nước", "internet", "wifi", "điện thoại", "tiền nhà", 
                "trọ", "tiền rác", "phí quản lý"
            ],
            "Giải trí": [
                "xem phim", "netflix", "spotify", "du lịch", "chơi game", 
                "bida", "karaoke", "nhạc"
            ],
            "Mua sắm": [
                "quần áo", "giày", "shopee", "lazada", "tiki", "mỹ phẩm", 
                "túi", "balo"
            ],
            "Sức khỏe": [
                "thuốc", "khám bệnh", "bảo hiểm", "phòng gym", "yoga", 
                "nha khoa", "massage"
            ]
        }
        
        self.compiled_rules = {}
        for category, keywords in self.category_mapping.items():
            pattern = r'\b(' + '|'.join(keywords) + r')\b'
            self.compiled_rules[category] = re.compile(pattern, re.IGNORECASE)

    def predict_category(self, description: str) -> str:
        if not description: return "Khác"
        
        # 👉 SỬ DỤNG HÀM IMPORT ĐỂ TIỀN XỬ LÝ
        cleaned_desc = clean_vietnamese_text(description)
        
        for category, pattern in self.compiled_rules.items():
            if pattern.search(cleaned_desc):
                return category
        return "Khác"

    def predict_category(self, description: str) -> str:
        if not description:
            return "Khác"
        
        # Áp dụng chuẩn hóa trước khi so khớp
        normalized_desc = normalize_vietnamese_text(description)
        
        for category, pattern in self.compiled_rules.items():
            if pattern.search(normalized_desc):
                return category
                
        return "Khác"

    def extract_amount(self, description: str) -> float:
        # Chuẩn hóa trước để xử lý Unicode, sau đó xóa toàn bộ khoảng trắng để bắt số
        normalized_desc = normalize_vietnamese_text(description)
        text = normalized_desc.replace(" ", "")
        
        match_k = re.search(r'(\d+)k', text)
        if match_k:
            return float(match_k.group(1)) * 1000
            
        match_tr = re.search(r'(\d+)tr(\d*)', text) or re.search(r'(\d+)củ(\d*)', text)
        if match_tr:
            millions = float(match_tr.group(1)) * 1000000
            hundred_thousands = float(match_tr.group(2)) * 100000 if match_tr.group(2) else 0
            return millions + hundred_thousands
            
        numbers = re.findall(r'\d+', text)
        if numbers:
            return float(max(numbers, key=int))
            
        return 0.0


# --- 2. MACHINE LEARNING CLASSIFIER ---
class MLClassifier:
    def __init__(self, model_path='app/ai/models/expense_model.pkl'):
        self.model_path = model_path
        self.pipeline = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_path):
            self.pipeline = joblib.load(self.model_path)
        else:
            # 👉 NÂNG CẤP TF-IDF VECTORIZER Ở ĐÂY
            self.pipeline = Pipeline([
                ('tfidf', TfidfVectorizer(
                    ngram_range=(1, 2),    # Bắt cụm từ (vd: "trà sữa", "cơm tấm" thay vì chỉ "trà", "sữa")
                    max_features=3000,     # Chỉ học 3000 từ/cụm từ phổ biến nhất (giúp model nhẹ và chạy nhanh)
                    min_df=2,              # Loại bỏ nhiễu: Từ phải xuất hiện ít nhất 2 lần trong toàn bộ data mới được học
                    sublinear_tf=True      # Scale logarit: Nếu người dùng gõ "ăn ăn ăn", hệ thống không bị đánh lừa là từ này quan trọng gấp 3 lần bình thường
                )),
                ('clf', MultinomialNB(
                    alpha=0.1              # Tinh chỉnh độ mượt (smoothing) giúp Naive Bayes phân loại tốt hơn với các từ hiếm
                ))
            ])

    def train_model(self, csv_file_path: str):
        try:
            df = pd.read_csv(csv_file_path)
            df = df.dropna(subset=['description', 'category'])
            
            # Áp dụng chuẩn hóa văn bản cho toàn bộ cột 'description' trước khi train
            df['description'] = df['description'].apply(normalize_vietnamese_text)
            
            X = df['description']
            y = df['category']
            
            self.pipeline.fit(X, y)
            
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.pipeline, self.model_path)
            self._load_model()
            
            return True, "Huấn luyện mô hình thành công!"
        except Exception as e:
            return False, f"Lỗi khi huấn luyện: {str(e)}"

    def predict_category(self, description: str) -> str:
        if not description:
            return "Khác"
            
        if not os.path.exists(self.model_path):
            return "Chưa huấn luyện"
            
        # Áp dụng chuẩn hóa trước khi dự đoán
        normalized_desc = normalize_vietnamese_text(description)
        prediction = self.pipeline.predict([normalized_desc])
        return prediction[0]
    def train_model(self, csv_file_path: str):
        try:
            df = pd.read_csv(csv_file_path)
            df = df.dropna(subset=['description', 'category'])
            
            # 👉 TIỀN XỬ LÝ TOÀN BỘ CỘT DATA TRƯỚC KHI TRAIN
            df['description'] = df['description'].apply(clean_vietnamese_text)
            
            X = df['description']
            y = df['category']
            
            self.pipeline.fit(X, y)
            # ... (Code lưu file model) ...
            return True, "Huấn luyện mô hình thành công!"
        except Exception as e:
            return False, f"Lỗi khi huấn luyện: {str(e)}"

    def predict_category(self, description: str) -> str:
        if not description: return "Khác"
        if not os.path.exists(self.model_path): return "Chưa huấn luyện"
            
        # 👉 TIỀN XỬ LÝ ĐẦU VÀO CỦA USER TRƯỚC KHI DỰ ĐOÁN
        cleaned_desc = clean_vietnamese_text(description)
        prediction = self.pipeline.predict([cleaned_desc])
        return prediction[0]


# --- TEST ---
if __name__ == "__main__":
    print("=== TEST RULE-BASED CÓ CHUẨN HÓA ===")
    rule_classifier = RuleBasedClassifier()
    
    # Cố tình viết hoa, viết thường lộn xộn, nhiều dấu cách
    test_rule_inputs = [
        "   Ăn CƠM TẤM   sườn  bì chả   35K ",
        "ĐỔ xăng XE MÁY  50000",
        "Thanh toán TIỀN ĐIỆN tháng này 1Tr2"
    ]
    
    for text in test_rule_inputs:
        cat = rule_classifier.predict_category(text)
        amt = rule_classifier.extract_amount(text)
        print(f"Gốc: '{text}'")
        print(f"-> Chuẩn hóa nội bộ thành: '{normalize_vietnamese_text(text)}'")
        print(f"-> Danh mục: {cat} | Tiền: {int(amt)} VNĐ\n")

    print("=== TEST ML CÓ CHUẨN HÓA ===")
    ml_classifier = MLClassifier(model_path='expense_model_test.pkl')
    
    mock_data = pd.DataFrame({
        'description': [
            'Mua bó rau VÀ thịt LỢN', 'Bát Phở Bò', 'Ly Trà ĐÀO cam sả', 
            'Tiền Xăng xe tay ga', 'Thay BÌNH nhớt', 
            'Đóng tiền MẠNG VNPT', 'Thanh toán TIỀN ĐIỆN',
            'Vé XEM phim CGV', 'Đi ĐÀ LẠT chơi'
        ],
        'category': [
            'Ăn uống', 'Ăn uống', 'Ăn uống', 
            'Đi lại', 'Đi lại', 
            'Hóa đơn', 'Hóa đơn',
            'Giải trí', 'Giải trí'
        ]
    })
    mock_data.to_csv('mock_training_data.csv', index=False)
    
    ml_classifier.train_model('mock_training_data.csv')
    
    test_ml_inputs = [
        "  MUA hai KÝ THỊT BÒ  ",
        "ĐÓNG   tiền wIfi VIETTEL",
    ]
    
    for text in test_ml_inputs:
        predicted_cat = ml_classifier.predict_category(text)
        print(f"Gốc: '{text}' -> AI Dự đoán: {predicted_cat}")
    
class LogisticRegressionClassifier:
    def __init__(self, model_path='app/ai/models/lr_expense_model.pkl'):
        self.model_path = model_path
        self.pipeline = None
        self._load_model()

    def _load_model(self):
        if os.path.exists(self.model_path):
            self.pipeline = joblib.load(self.model_path)
        else:
            # Pipeline sử dụng Logistic Regression thay vì Naive Bayes
            self.pipeline = Pipeline([
                ('tfidf', TfidfVectorizer(
                    ngram_range=(1, 2), 
                    max_features=3000, 
                    min_df=2, 
                    sublinear_tf=True
                )),
                ('clf', LogisticRegression(
                    C=1.0,                     # Tham số điều chuẩn (Regularization), chống học vẹt (Overfitting)
                    class_weight='balanced',   # Tự động cân bằng nếu dữ liệu các danh mục không đều nhau
                    max_iter=1000,             # Tăng số vòng lặp tối đa để thuật toán hội tụ tốt hơn
                    random_state=42            # Cố định random seed để kết quả ổn định
                ))
            ])

    def train_model(self, csv_file_path: str):
        try:
            df = pd.read_csv(csv_file_path)
            df = df.dropna(subset=['description', 'category'])
            
            # Áp dụng tiền xử lý (Sử dụng hàm clean_vietnamese_text đã import ở các bước trước)
            df['description'] = df['description'].apply(clean_vietnamese_text)
            
            X = df['description']
            y = df['category']
            
            self.pipeline.fit(X, y)
            
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.pipeline, self.model_path)
            self._load_model()
            
            return True, "Huấn luyện mô hình Logistic Regression thành công!"
        except Exception as e:
            return False, f"Lỗi khi huấn luyện LR: {str(e)}"

    def predict_category(self, description: str) -> str:
        if not description: return "Khác"
        if not os.path.exists(self.model_path): return "Chưa huấn luyện"
            
        cleaned_desc = clean_vietnamese_text(description)
        prediction = self.pipeline.predict([cleaned_desc])
        return prediction[0]
        
    def predict_proba(self, description: str):
        """
        [Tính năng nâng cao của Logistic Regression]
        Trả về độ tự tin (xác suất phần trăm) của từng danh mục thay vì chỉ trả về kết quả.
        """
        if not description or not os.path.exists(self.model_path): return None
        
        cleaned_desc = clean_vietnamese_text(description)
        probs = self.pipeline.predict_proba([cleaned_desc])[0]
        classes = self.pipeline.classes_
        
        # Ghép danh mục và xác suất thành dictionary (vd: {'Ăn uống': 0.85, 'Mua sắm': 0.10, ...})
        return dict(zip(classes, probs))