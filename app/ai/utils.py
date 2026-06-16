import re
import unicodedata

def normalize_vietnamese_text(text: str) -> str:
    """
    Hàm chuẩn hóa văn bản tiếng Việt cơ bản:
    - Chuyển về chữ thường (lowercase)
    - Chuẩn hóa Unicode (tránh lỗi gõ dấu kiểu cũ/mới như 'oá' vs 'óa')
    - Xóa các ký tự đặc biệt, icon, số tài khoản, chỉ giữ lại chữ và khoảng trắng
    - Xóa khoảng trắng thừa
    """
    if not text:
        return ""
    
    # 1. Chuyển về chữ thường
    text = text.lower()
    
    # 2. Chuẩn hóa Unicode dựng sẵn (NFC) giúp đồng nhất cách lưu trữ dấu tiếng Việt
    text = unicodedata.normalize('NFC', text)
    
    # 3. Thay thế các ký tự xuống dòng, tab thành khoảng trắng
    text = re.sub(r'\s+', ' ', text)
    
    # 4. Loại bỏ số tài khoản, mã giao dịch dạng số (ví dụ: "ft23234234" -> "ft")
    # Giữ lại chữ cái tiếng Việt và khoảng trắng (bao gồm cả các ký tự có dấu)
    # Regex này giữ lại chữ thường abc..., các ký tự có dấu tiếng Việt và khoảng trắng
    text = re.sub(r'[^a-zA-Zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễđìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹ\s]', '', text)
    
    # 5. Xóa khoảng trắng ở đầu và cuối chuỗi, thu gọn nhiều khoảng trắng ở giữa
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    
    return text