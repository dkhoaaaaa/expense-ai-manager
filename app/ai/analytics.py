import pandas as pd
import numpy as np

class ExpenseAnalyzer:
    def __init__(self):
        pass

    def analyze_spending_trends(self, transactions: list) -> dict:
        """
        Phân tích xu hướng Tăng/Giảm (Month-over-Month).
        Input: List các giao dịch [{'date': '2023-10-15', 'amount': 500000, 'category': 'Ăn uống'}, ...]
        """
        if not transactions:
            return {"status": "error", "message": "Không có dữ liệu để phân tích"}

        try:
            # 1. Khởi tạo DataFrame
            df = pd.DataFrame(transactions)
            df['date'] = pd.to_datetime(df['date'])
            
            # 2. Tạo cột Tháng-Năm (VD: 2023-10)
            df['month'] = df['date'].dt.to_period('M')
            
            # Sắp xếp các tháng theo thứ tự thời gian
            months = sorted(df['month'].unique())
            
            if len(months) < 2:
                return {
                    "status": "insufficient_data", 
                    "message": "Chưa đủ dữ liệu để phân tích xu hướng.",
                    "data": None
                }

            # Lấy tháng mới nhất (Hiện tại) và tháng sát trước nó
            current_month = months[-1]
            prev_month = months[-2]

            # ---------------------------------------------------------
            # PHẦN 1: PHÂN TÍCH TỔNG QUAN (OVERALL TREND)
            # ---------------------------------------------------------
            monthly_totals = df.groupby('month')['amount'].sum()
            current_total = monthly_totals.get(current_month, 0)
            prev_total = monthly_totals.get(prev_month, 0)
            
            # Tính phần trăm thay đổi (Tránh lỗi chia cho 0)
            if prev_total == 0:
                overall_change_pct = 100.0 if current_total > 0 else 0.0
            else:
                overall_change_pct = ((current_total - prev_total) / prev_total) * 100

            overall_trend = "tăng" if overall_change_pct > 0 else "giảm" if overall_change_pct < 0 else "không đổi"

            # ---------------------------------------------------------
            # PHẦN 2: PHÂN TÍCH BÓC TÁCH TỪNG DANH MỤC (CATEGORY BREAKDOWN)
            # ---------------------------------------------------------
            # Tính tổng tiền từng danh mục của 2 tháng
            cat_current = df[df['month'] == current_month].groupby('category')['amount'].sum()
            cat_prev = df[df['month'] == prev_month].groupby('category')['amount'].sum()

            # Gộp dữ liệu 2 tháng lại với nhau (Điền 0 nếu tháng đó không có chi tiêu cho danh mục này)
            cat_comparison = pd.DataFrame({'current': cat_current, 'prev': cat_prev}).fillna(0)
            
            category_trends = []
            for category, row in cat_comparison.iterrows():
                cur_amt = row['current']
                prv_amt = row['prev']
                
                if prv_amt == 0:
                    change_pct = 100.0 if cur_amt > 0 else 0.0
                else:
                    change_pct = ((cur_amt - prv_amt) / prv_amt) * 100

                trend_dir = "tăng" if change_pct > 0 else "giảm" if change_pct < 0 else "không đổi"
                
                category_trends.append({
                    "category": category,
                    "current_amount": int(cur_amt),
                    "prev_amount": int(prv_amt),
                    "difference": int(cur_amt - prv_amt), # Số tiền chênh lệch
                    "change_percentage": round(abs(change_pct), 2),
                    "trend": trend_dir
                })

            # Sắp xếp danh mục: Cái nào làm TĂNG chi tiêu nhiều nhất sẽ nằm trên cùng
            category_trends.sort(key=lambda x: x['difference'], reverse=True)

            # ---------------------------------------------------------
            # TẠO INSIGHT (THÔNG ĐIỆP GỢI Ý CHO NGƯỜI DÙNG)
            # ---------------------------------------------------------
            insight_message = f"Tổng chi tiêu tháng này đã {overall_trend} {abs(overall_change_pct):.1f}% so với tháng trước."
            
            # Cảnh báo danh mục vung tay quá trán
            top_increase = category_trends[0]
            if top_increase['trend'] == 'tăng' and top_increase['difference'] > 0:
                warning = f"⚠️ Cảnh báo: Chi tiêu cho '{top_increase['category']}' đã tăng {top_increase['change_percentage']}% (+{top_increase['difference']:,} VNĐ). Bạn nên cân nhắc hạn chế lại."
            else:
                warning = "🎉 Chúc mừng! Bạn đang kiểm soát chi tiêu các danh mục rất tốt."

            return {
                "status": "success",
                "data": {
                    "comparison_months": {
                        "current_month": str(current_month),
                        "previous_month": str(prev_month)
                    },
                    "overall": {
                        "current_total": int(current_total),
                        "prev_total": int(prev_total),
                        "difference": int(current_total - prev_total),
                        "change_percentage": round(abs(overall_change_pct), 2),
                        "trend": overall_trend,
                        "insight": insight_message,
                        "warning": warning
                    },
                    "category_breakdown": category_trends
                }
            }

        except Exception as e:
            return {"status": "error", "message": f"Lỗi phân tích xu hướng: {str(e)}"}
    def analyze_time_series_trend(self, transactions: list, window_size: int = 3) -> dict:
        """
        Phân tích chuỗi thời gian để tìm xu hướng dài hạn bằng Moving Average.
        Output được thiết kế chuẩn cấu trúc để nạp thẳng vào Chart.js trên Frontend.
        """
        if not transactions:
            return {"status": "error", "message": "Không có dữ liệu để phân tích chuỗi thời gian"}

        try:
            # 1. Chuyển đổi dữ liệu và nhóm theo tháng
            df = pd.DataFrame(transactions)
            df['date'] = pd.to_datetime(df['date'])
            
            # Tạo chuỗi định dạng YYYY-MM để dễ hiển thị
            df['month_label'] = df['date'].dt.strftime('%Y-%m')
            
            # Gom tổng tiền theo từng tháng và sắp xếp theo thời gian
            time_series = df.groupby('month_label')['amount'].sum().reset_index()
            time_series = time_series.sort_values('month_label')
            
            if len(time_series) < window_size:
                return {
                    "status": "error", 
                    "message": f"Cần ít nhất {window_size} tháng dữ liệu để vẽ đường xu hướng trung bình động."
                }

            # 2. Tính toán đường Trung bình động (Moving Average)
            # min_periods=1 giúp tính cả những tháng đầu tiên dù chưa đủ chu kỳ (window_size)
            time_series['moving_average'] = time_series['amount'].rolling(
                window=window_size, min_periods=1
            ).mean().round(0)

            # 3. Phân tích độ dốc của toàn bộ chuỗi (Linear Trend)
            # Dùng numpy polyfit (Hồi quy bậc 1) để xem chiều hướng chung là cắm đầu xuống hay đi lên
            x_indices = np.arange(len(time_series))
            y_values = time_series['amount'].values
            slope, _ = np.polyfit(x_indices, y_values, 1) # Bậc 1: y = ax + b (lấy a là slope)

            if slope > 50000:  # Tăng trung bình > 50k mỗi tháng
                long_term_trend = "upward"
                insight = "Xu hướng dài hạn: Chi tiêu của bạn đang TĂNG DẦN qua các tháng. Hãy chú ý tiết kiệm!"
            elif slope < -50000: # Giảm trung bình > 50k mỗi tháng
                long_term_trend = "downward"
                insight = "Xu hướng dài hạn: Tuyệt vời! Bạn đang GIẢM DẦN chi tiêu và tiết kiệm tốt hơn."
            else:
                long_term_trend = "stable"
                insight = "Xu hướng dài hạn: Mức chi tiêu của bạn đang khá ỔN ĐỊNH."

            # 4. Định dạng dữ liệu chuẩn JSON để Frontend vẽ biểu đồ (Chart.js ready)
            return {
                "status": "success",
                "meta": {
                    "long_term_trend": long_term_trend,
                    "insight": insight,
                    "slope": int(slope) # Tốc độ tăng/giảm mỗi tháng
                },
                "chart_data": {
                    "labels": time_series['month_label'].tolist(),
                    "datasets": [
                        {
                            "label": "Chi tiêu thực tế (VNĐ)",
                            "type": "bar",
                            "data": time_series['amount'].astype(int).tolist()
                        },
                        {
                            "label": f"Đường xu hướng (Trung bình động {window_size} tháng)",
                            "type": "line",
                            "data": time_series['moving_average'].astype(int).tolist()
                        }
                    ]
                }
            }

        except Exception as e:
            return {"status": "error", "message": f"Lỗi xử lý chuỗi thời gian: {str(e)}"}