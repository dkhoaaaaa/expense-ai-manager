import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

class ExpensePredictor:
    def __init__(self):
        # Khởi tạo mô hình Hồi quy tuyến tính
        self.model = LinearRegression()

    def forecast_next_month(self, transactions: list) -> dict:
        """
        Dự báo tổng chi tiêu tháng tiếp theo dựa trên lịch sử giao dịch.
        Đầu vào: Danh sách dictionary chứa 'date' (YYYY-MM-DD) và 'amount' (float/int).
        """
        if not transactions:
            return {"status": "error", "message": "Không có dữ liệu giao dịch để dự báo"}

        try:
            # 1. Chuyển đổi dữ liệu thành Pandas DataFrame
            df = pd.DataFrame(transactions)
            df['date'] = pd.to_datetime(df['date'])
            
            # 2. Gom nhóm tổng số tiền chi tiêu theo từng tháng
            # dt.to_period('M') giúp gộp các ngày trong cùng 1 tháng thành 1 dòng
            monthly_expenses = df.groupby(df['date'].dt.to_period('M'))['amount'].sum().reset_index()
            
            # 3. Kiểm tra số lượng dữ liệu
            if len(monthly_expenses) < 2:
                # Nếu mới dùng app được 1 tháng, chưa thể vẽ đường xu hướng -> Lấy chính số đó
                avg_amount = int(monthly_expenses['amount'].mean())
                return {
                    "status": "success",
                    "predicted_amount": avg_amount,
                    "method": "Average (Insufficient History)",
                    "trend": "neutral",
                    "difference_from_last_month": 0,
                    "message": "Cần ít nhất 2 tháng để AI phân tích xu hướng. Hiện đang trả về mức chi tiêu trung bình."
                }

            # 4. Chuẩn bị dữ liệu cho Machine Learning
            # X là trục hoành (tháng thứ 0, 1, 2...), y là trục tung (số tiền)
            monthly_expenses['month_index'] = np.arange(len(monthly_expenses))
            X = monthly_expenses[['month_index']]
            y = monthly_expenses['amount']

            # 5. Huấn luyện mô hình tìm đường xu hướng
            self.model.fit(X, y)

            # 6. Dự báo cho tháng tiếp theo (tháng có index = độ dài hiện tại)
            next_month_index = pd.DataFrame([[len(monthly_expenses)]], columns=['month_index'])
            predicted_amount = self.model.predict(next_month_index)[0]

            # Không cho phép dự báo ra số âm (nếu chi tiêu đang giảm quá nhanh)
            predicted_amount = max(0, int(predicted_amount))

            # 7. Phân tích thêm xu hướng (Analytics)
            last_month_amount = int(y.iloc[-1])
            difference = abs(predicted_amount - last_month_amount)
            
            if predicted_amount > last_month_amount:
                trend = "up" # Bội chi (Tăng)
            elif predicted_amount < last_month_amount:
                trend = "down" # Tiết kiệm (Giảm)
            else:
                trend = "neutral"

            return {
                "status": "success",
                "predicted_amount": predicted_amount,
                "method": "Linear Regression",
                "trend": trend,
                "difference_from_last_month": difference,
                "historical_data_months": len(monthly_expenses),
                "message": f"AI dự báo tháng tới bạn sẽ chi tiêu khoảng {predicted_amount:,} VNĐ"
            }

        except Exception as e:
            return {"status": "error", "message": f"Lỗi tiền xử lý dữ liệu: {str(e)}"}