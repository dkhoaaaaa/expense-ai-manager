import os
import google.generativeai as genai
from app.services.user.userHomeService import UserHomeService

class AIService:
    @staticmethod
    def generate_response(user_id, user_message):
        """
        Lấy thông tin tài chính của người dùng, tạo prompt context và gửi tới Gemini API.
        """
        # 1. Lấy dữ liệu tài chính thực tế từ database của user
        financial_data = UserHomeService.getHomeData(user_id)
        
        # 2. Phân tích và xây dựng dữ liệu context
        user_name = financial_data.get("user", {}).get("hoTen", "Người dùng")
        stats = financial_data.get("stats", {})
        balance = stats.get("soDu", 0.0)
        income = stats.get("thuNhapThang", 0.0)
        expense = stats.get("chiTieuThang", 0.0)
        
        # Top danh mục chi tiêu
        top_categories = financial_data.get("topDanhMucChiTieu", [])
        top_cat_str = ""
        for cat in top_categories:
            top_cat_str += f"- {cat['tenDanhMuc']}: {cat['tongTien']:,.0f}đ ({cat['tyLe']}%)\n"
            
        # Ngân sách & Tiến độ
        budgets = financial_data.get("nganSach", [])
        budget_str = ""
        for b in budgets:
            budget_str += f"- {b['tenDanhMuc']}: Hạn mức {b['hanMuc']:,.0f}đ, đã dùng {b['daDung']:,.0f}đ ({b['tyLe']}%)\n"
            
        # Giao dịch gần đây
        recent_txs = financial_data.get("giaoDichGanDay", [])
        tx_str = ""
        for tx in recent_txs:
            loai_str = "Thu nhập" if tx["loai"] == "THU" else "Chi tiêu"
            tx_str += f"- {tx['ngayGiaoDich']}: {tx['moTa']} | {loai_str} | {tx['soTien']:,.0f}đ ({tx['tenDanhMuc']})\n"
            
        # 3. Xây dựng prompt context hoàn chỉnh
        system_instruction = (
            "Bạn là một chuyên gia tư vấn tài chính cá nhân AI thân thiện, thông thái và chuyên nghiệp của ứng dụng Expense AI.\n"
            f"Người dùng hiện tại bạn đang hỗ trợ là: {user_name}.\n"
            "Dưới đây là thông tin tài chính hiện có trong cơ sở dữ liệu của người dùng này (tháng 6 năm 2026):\n"
            f"- Số dư tài khoản hiện tại: {balance:,.0f}đ\n"
            f"- Tổng thu nhập tháng này: {income:,.0f}đ\n"
            f"- Tổng chi tiêu tháng này: {expense:,.0f}đ\n\n"
            "Danh mục chi tiêu hàng đầu trong tháng:\n"
            f"{top_cat_str if top_cat_str else 'Chưa phát sinh chi tiêu nào.'}\n"
            "Ngân sách và hạn mức chi tiêu đã thiết lập:\n"
            f"{budget_str if budget_str else 'Chưa có ngân sách nào được thiết lập cho tháng này.'}\n"
            "5 giao dịch gần nhất:\n"
            f"{tx_str if tx_str else 'Không có giao dịch nào gần đây.'}\n\n"
            "Yêu cầu:\n"
            "1. Luôn phản hồi bằng tiếng Việt lịch sự, xưng hô 'tôi' và 'bạn' hoặc 'anh/chị' một cách tự nhiên.\n"
            "2. Trả lời trực tiếp vào câu hỏi của người dùng. Hãy sử dụng các số liệu tài chính của người dùng ở trên để phân tích và đưa ra ví dụ/lời khuyên cụ thể, thực tế thay vì trả lời chung chung.\n"
            "3. Giữ câu trả lời ngắn gọn, súc tích (dưới 250 từ) để phù hợp hiển thị trong bong bóng chat nhỏ.\n"
            "4. Sử dụng định dạng Markdown (như in đậm **, danh sách -, dòng kẻ) để làm câu trả lời rõ ràng và dễ đọc."
        )
        
        # 4. Lấy API Key từ biến môi trường
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "Tính năng Chatbot yêu cầu cấu hình GEMINI_API_KEY trong file .env ở thư mục gốc."
            )
            
        # Cấu hình Google GenAI
        genai.configure(api_key=api_key)
        
        # 5. Cấu hình an toàn (Safety Settings) để tránh nội dung độc hại (CWE-1188)
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
        
        # Sử dụng model gemini-1.5-flash truyền trực tiếp system_instruction (CWE-1188)
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            system_instruction=system_instruction
        )
        
        # 6. Gọi API sinh nội dung bọc trong try-except để bắt lỗi mạng/API (CWE-754)
        try:
            response = model.generate_content(
                user_message,
                safety_settings=safety_settings
            )
        except Exception as api_err:
            raise Exception(f"Không thể kết nối hoặc gọi API Gemini: {str(api_err)}")
        
        if not response or not response.text:
            raise Exception("Không nhận được phản hồi từ Gemini API. Vui lòng thử lại sau.")
            
        return response.text

