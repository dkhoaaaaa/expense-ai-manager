from flask import request, jsonify
from app.ai.predictor import ExpensePredictor
from app.ai.predictor import ExpensePredictor
from app.ai.analytics import ExpenseAnalyzer
# Khởi tạo Predictor Global
predictor = ExpensePredictor()

def forecast_expense_api():
    """
    API Endpoint: /api/analytics/forecast
    Method: POST
    Nhận mảng lịch sử giao dịch từ Database (thường do Frontend gọi lên kèm Data, 
    hoặc Backend tự query DB rồi đẩy vào model).
    """
    try:
        data = request.get_json()
        
        # Lấy danh sách giao dịch (nếu Frontend gửi lên)
        transactions = data.get('transactions', [])
        
        if not transactions:
            # Lưu ý thực tế: Thay vì bắt Frontend gửi, ở đây bạn có thể dùng SQLAlchemy 
            # để tự động query DB lấy các giao dịch của User_ID hiện tại.
            return jsonify({"status": "error", "message": "Thiếu dữ liệu lịch sử"}), 400
            
        # Gọi mô hình AI
        result = predictor.forecast_next_month(transactions)
        
        if result['status'] == 'error':
            return jsonify(result), 400
            
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Lỗi Server: {str(e)}"}), 500
    # Khởi tạo các class ở cấp toàn cục (Global) để tái sử dụng
predictor = ExpensePredictor()
analyzer = ExpenseAnalyzer()

def forecast_expense():
    """
    API Endpoint: /api/analytics/forecast
    Method: POST
    Dự báo chi tiêu tháng tiếp theo dựa trên lịch sử.
    """
    try:
        data = request.get_json()
        transactions = data.get('transactions', [])
        
        if not transactions:
            return jsonify({"status": "error", "message": "Yêu cầu cung cấp danh sách giao dịch ('transactions')"}), 400
            
        result = predictor.forecast_next_month(transactions)
        
        if result.get('status') == 'error':
            return jsonify(result), 400
            
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Lỗi Server (Forecast): {str(e)}"}), 500


def analyze_mom_trend():
    """
    API Endpoint: /api/analytics/trend/mom
    Method: POST
    Phân tích so sánh chi tiêu giữa tháng này và tháng trước (Month-over-Month).
    Giúp phát hiện danh mục nào đang tiêu tốn nhiều tiền nhất.
    """
    try:
        data = request.get_json()
        transactions = data.get('transactions', [])
        
        if not transactions:
            return jsonify({"status": "error", "message": "Yêu cầu cung cấp danh sách giao dịch ('transactions')"}), 400
            
        result = analyzer.analyze_spending_trends(transactions)
        
        if result.get('status') == 'error':
            return jsonify(result), 400
        if result.get('status') == 'insufficient_data':
            return jsonify(result), 200
            
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Lỗi Server (MoM Trend): {str(e)}"}), 500


def analyze_timeseries_trend():
    """
    API Endpoint: /api/analytics/trend/timeseries
    Method: POST
    Phân tích xu hướng dài hạn (đường trung bình động) để vẽ biểu đồ Chart.js.
    """
    try:
        data = request.get_json()
        transactions = data.get('transactions', [])
        
        # Cho phép Frontend tùy chỉnh chu kỳ trung bình động (mặc định là 3 tháng)
        window_size = int(data.get('window_size', 3))
        
        if not transactions:
            return jsonify({"status": "error", "message": "Yêu cầu cung cấp danh sách giao dịch ('transactions')"}), 400
            
        result = analyzer.analyze_time_series_trend(transactions, window_size=window_size)
        
        if result.get('status') == 'error':
            return jsonify(result), 400
            
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Lỗi Server (Time-series Trend): {str(e)}"}), 500