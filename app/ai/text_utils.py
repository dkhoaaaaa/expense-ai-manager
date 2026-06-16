import re
import unicodedata

def clean_vietnamese_text(text: str) -> str:
    """
    Hàm tiền xử lý và làm sạch văn bản tiếng Việt chuyên sâu cho NLP.
    """
    if not isinstance(text, str):
        return ""
        
    # 1. Chuẩn hóa Unicode (Đưa về chuẩn NFC để tránh lỗi font chữ)
    text = unicodedata.normalize('NFC', text)
    
    # 2. Chuyển thành chữ thường
    text = text.lower()
    
    # 3. Xóa các ký tự đặc biệt, dấu câu (Chỉ giữ lại chữ cái và số)
    # Regex \w giữ lại chữ và số, \s giữ lại khoảng trắng
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # 4. (Tùy chọn) Xóa stop words cơ bản của chi tiêu
    # Các từ như "và", "những", "các", "cho" thường không mang nhiều ý nghĩa phân loại
    stopwords = ['và', 'cho', 'những', 'các', 'của', 'là', 'thì', 'mà', 'với']
    words = text.split()
    words = [w for w in words if w not in stopwords]
    text = ' '.join(words)
    
    # 5. Xóa khoảng trắng thừa (Đưa nhiều khoảng trắng về 1)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

# --- TEST NHANH ---
if __name__ == "__main__":
    raw_text = "   Mua bó rau, và 2 kg thịt lợn!!! 🐷 cho bữa tối.  "
    print(f"Gốc: '{raw_text}'")
    print(f"Đã xử lý: '{clean_vietnamese_text(raw_text)}'")
    # Kết quả sẽ là: 'mua bó rau 2 kg thịt lợn bữa tối'