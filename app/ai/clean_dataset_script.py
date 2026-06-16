import pandas as pd
import os

# Import hàm làm sạch
from text_utils import clean_vietnamese_text

def preprocess_csv_dataset(input_csv: str, output_csv: str):
    """
    Đọc file CSV thô, làm sạch toàn bộ cột 'description' và lưu ra file mới.
    """
    print(f"Đang đọc dữ liệu thô từ: {input_csv} ...")
    
    if not os.path.exists(input_csv):
        print("Lỗi: Không tìm thấy file đầu vào!")
        return
        
    df = pd.read_csv(input_csv)
    
    # Kiểm tra xem có cột description không
    if 'description' not in df.columns:
        print("Lỗi: File CSV phải có cột 'description'")
        return
        
    # Thống kê trước khi xử lý
    print(f"Tổng số dòng ban đầu: {len(df)}")
    df = df.dropna(subset=['description']) # Xóa dòng rỗng
    
    print("Đang chạy tiền xử lý văn bản (NLP Preprocessing)...")
    # Áp dụng hàm clean_vietnamese_text cho toàn bộ Series (cột)
    df['description'] = df['description'].apply(clean_vietnamese_text)
    
    # Loại bỏ các dòng mà sau khi làm sạch chỉ còn chuỗi rỗng (vd: dòng gốc chỉ toàn emoji "😂😂")
    df = df[df['description'].str.strip().astype(bool)]
    
    # Lưu ra file mới
    df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"Thành công! Đã lưu dữ liệu sạch ra: {output_csv}")
    print(f"Tổng số dòng giữ lại: {len(df)}")

# --- THỰC THI ---
if __name__ == "__main__":
    # Giả sử bạn có file dữ liệu thô tải từ database về
    raw_file = "raw_transactions_from_db.csv"
    clean_file = "clean_training_data.csv"
    
    # Tạo một file thô giả lập để test
    pd.DataFrame({
        "description": [
            "  Ăn phở gà!!! 🍜 ", 
            "Tiền điện tháng 10... quá mắc", 
            "🎉 Mua quà cho NY", 
            "  " # Dòng lỗi, toàn khoảng trắng
        ],
        "category": ["Ăn uống", "Hóa đơn", "Mua sắm", "Khác"]
    }).to_csv(raw_file, index=False)
    
    preprocess_csv_dataset(raw_file, clean_file)