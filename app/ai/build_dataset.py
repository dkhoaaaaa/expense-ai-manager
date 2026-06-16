import random
import pandas as pd
import os

# Import class MLClassifier từ file classifier.py của bạn
from classifier import MLClassifier

def generate_synthetic_transactions(num_samples=2000):
    """
    Hàm sinh dữ liệu giao dịch giả lập tự động.
    Tạo ra các câu văn ngẫu nhiên kết hợp từ Hành động + Đối tượng + Thông tin phụ.
    """
    
    # 1. Từ điển dữ liệu thô (Càng nhiều từ, AI học càng thông minh)
    data_components = {
        "Ăn uống": {
            "actions": ["ăn", "uống", "mua", "đặt", "nhậu", ""],
            "items": ["cơm tấm", "phở bò", "bún đậu", "trà sữa", "cafe", "bánh mì", "nước ép", "đồ ăn vặt", "lẩu", "highlands", "shopee food", "thịt", "rau", "trái cây", "hải sản"],
            "extras": ["sáng", "trưa", "tối", "cùng bạn", "công ty", "vỉa hè", ""]
        },
        "Đi lại": {
            "actions": ["đổ", "đi", "đặt", "thay", "rửa", "bảo dưỡng", ""],
            "items": ["xăng", "grab", "bebike", "taxi", "xe ôm", "nhớt", "vé xe buýt", "vé tàu", "xe máy", "gửi xe"],
            "extras": ["đi làm", "về quê", "tháng này", "dọc đường", ""]
        },
        "Hóa đơn": {
            "actions": ["đóng", "thanh toán", "chuyển khoản", "trả", ""],
            "items": ["tiền điện", "tiền nước", "internet", "wifi vnpt", "cước viettel", "tiền nhà", "tiền trọ", "phí quản lý", "tiền rác"],
            "extras": ["tháng này", "kỳ 1", "qua momo", "banking", ""]
        },
        "Giải trí": {
            "actions": ["xem", "mua", "gia hạn", "chơi", "đi", ""],
            "items": ["phim cgv", "netflix", "spotify", "youtube premium", "bida", "karaoke", "du lịch", "đà lạt", "game", "steam"],
            "extras": ["cuối tuần", "với bồ", "cùng team", "giải stress", ""]
        },
        "Mua sắm": {
            "actions": ["mua", "order", "săn sale", "chốt đơn", ""],
            "items": ["quần áo", "giày", "áo thun", "mỹ phẩm", "kem chống nắng", "shopee", "lazada", "túi xách", "balo", "ốp lưng"],
            "extras": ["tặng sn", "mới", "sale 11/11", "freeship", ""]
        },
        "Sức khỏe": {
            "actions": ["mua", "khám", "đóng", "tập", "đi", ""],
            "items": ["thuốc cảm", "bảo hiểm y tế", "phòng gym", "yoga", "nha khoa", "nhổ răng", "massage", "vitamin", "bệnh viện"],
            "extras": ["định kỳ", "cho mẹ", "tháng", "bị ốm", ""]
        }
    }

    # 2. Các đuôi số tiền ngẫu nhiên để câu văn tự nhiên hơn
    amounts = ["35k", "50k", "100k", "1tr", "2tr5", "50000", "150.000", ""]

    dataset = []

    # 3. Vòng lặp sinh dữ liệu
    for _ in range(num_samples):
        # Chọn ngẫu nhiên một danh mục
        category = random.choice(list(data_components.keys()))
        components = data_components[category]
        
        # Chọn ngẫu nhiên các thành phần câu
        action = random.choice(components["actions"])
        item = random.choice(components["items"])
        extra = random.choice(components["extras"])
        amount = random.choice(amounts)
        
        # Ghép thành câu hoàn chỉnh và dọn dẹp khoảng trắng thừa
        description = f"{action} {item} {extra} {amount}"
        description = " ".join(description.split()) # Xóa khoảng trắng kép
        
        dataset.append({
            "description": description,
            "category": category
        })

    # Chuyển đổi thành DataFrame và xáo trộn dữ liệu (shuffle)
    df = pd.DataFrame(dataset)
    df = df.sample(frac=1).reset_index(drop=True)
    return df

# --- THỰC THI CHƯƠNG TRÌNH ---
if __name__ == "__main__":
    print("🚀 Bắt đầu quá trình xây dựng dữ liệu và huấn luyện AI...")
    
    # 1. Sinh 3000 dòng dữ liệu giả lập
    csv_filename = "large_training_data.csv"
    print(f"1. Đang tạo 3000 dòng dữ liệu giao dịch mẫu...")
    df_synthetic = generate_synthetic_transactions(num_samples=3000)
    df_synthetic.to_csv(csv_filename, index=False, encoding='utf-8')
    print(f"   -> Đã lưu dữ liệu ra file: {csv_filename}")
    
    # In thử 5 dòng đầu tiên để kiểm tra
    print("\n   [Xem trước 5 dòng dữ liệu]:")
    print(df_synthetic.head(5).to_string(index=False))
    print("-" * 50)
    
    # 2. Khởi tạo và huấn luyện mô hình (Import từ file classifier.py)
    print("2. Đang nạp dữ liệu vào mô hình Machine Learning...")
    # Khai báo đường dẫn lưu model, vd: 'models/expense_model.pkl'
    model_path = os.path.join(os.path.dirname(__file__), 'models', 'expense_model.pkl')
    ml_classifier = MLClassifier(model_path=model_path)
    
    # Gọi hàm train_model (Hàm này đã tích hợp sẵn normalize_vietnamese_text bên trong)
    success, msg = ml_classifier.train_model(csv_filename)
    
    if success:
        print(f"   -> 🎉 {msg}")
        
        # 3. Kiểm thử độ thông minh của mô hình với những câu khó/hiếm
        print("\n3. Kiểm thử với dữ liệu người dùng thực tế nhập vào:")
        test_cases = [
            "trà đào cam sả size L 45k",          # Món ăn cụ thể
            "chốt đơn shopee sale giữa tháng",    # Không có từ mua sắm trực tiếp
            "nhổ răng khôn bv răng hàm mặt",      # Y tế chuyên sâu
            "cà thẻ cgv landmark",                # Tên riêng rạp phim
            "tiền điện kỳ 2 tháng này 800 ngàn"   # Hóa đơn phức tạp
        ]
        
        for text in test_cases:
            pred = ml_classifier.predict_category(text)
            print(f"   + '{text}' ==> [ {pred} ]")
    else:
        print(f"   -> ❌ Thất bại: {msg}")