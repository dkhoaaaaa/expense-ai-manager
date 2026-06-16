import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# 👉 Import class Phân tích Xu hướng từ file analytics.py của bạn
from analytics import ExpenseAnalyzer

def generate_spending_trend_chart(transactions: list, window_size: int = 3, save_path: str = None):
    """
    Hàm vẽ biểu đồ xu hướng chi tiêu bằng Python.
    Kết hợp Biểu đồ Cột (Chi tiêu thực tế) và Biểu đồ Đường (Trung bình động).
    """
    print("⏳ Đang phân tích dữ liệu và vẽ biểu đồ...")
    
    # 1. Gọi hàm phân tích chuỗi thời gian đã xây dựng trước đó
    analyzer = ExpenseAnalyzer()
    result = analyzer.analyze_time_series_trend(transactions, window_size)
    
    if result.get('status') != 'success':
        print(f"❌ Lỗi: {result.get('message')}")
        return
        
    # 2. Bóc tách dữ liệu chuẩn bị vẽ
    chart_data = result['chart_data']
    labels = chart_data['labels'] # Danh sách các tháng ['2023-01', '2023-02', ...]
    
    # Dataset 0 là Cột (Thực tế), Dataset 1 là Đường (Trung bình động)
    actual_data = chart_data['datasets'][0]['data'] 
    trend_data = chart_data['datasets'][1]['data']
    
    meta = result['meta']
    
    # 3. Cấu hình khung biểu đồ (Figure)
    plt.figure(figsize=(10, 6)) # Kích thước 10x6 inch
    
    # Vẽ Biểu đồ Cột (Bar Chart) - Thể hiện chi tiêu từng tháng
    plt.bar(labels, actual_data, color='#4A90E2', alpha=0.7, label='Chi tiêu thực tế', width=0.5)
    
    # Vẽ Biểu đồ Đường (Line Chart) - Thể hiện xu hướng trung bình
    plt.plot(labels, trend_data, color='#E74C3C', marker='o', linewidth=2.5, 
             markersize=8, label=f'Xu hướng (Trung bình động {window_size} tháng)')
    
    # 4. Trang trí biểu đồ (Labels, Title, Grid)
    plt.title('BIỂU ĐỒ XU HƯỚNG CHI TIÊU HÀNG THÁNG', fontsize=14, fontweight='bold', pad=20)
    plt.xlabel('Tháng', fontsize=11, fontweight='bold')
    plt.ylabel('Số tiền (VNĐ)', fontsize=11, fontweight='bold')
    
    # Cài đặt lưới (Grid) mờ ở nền trục Y cho dễ nhìn
    plt.grid(axis='y', linestyle='--', alpha=0.4)
    
    # 5. Format số trục Y cho dễ đọc (VD: 5,000,000 -> 5.0 Tr)
    def millions_formatter(x, pos):
        return f'{x / 1000000:.1f} Tr'
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(millions_formatter))
    
    # Thêm ghi chú (Insight) của AI vào góc biểu đồ
    plt.annotate(
        meta['insight'], 
        xy=(0.02, -0.15), xycoords='axes fraction',
        fontsize=10, color='#2C3E50', style='italic'
    )

    # Đặt Legend (Bảng chú giải)
    plt.legend(loc='upper right')
    
    # Tự động căn chỉnh lề
    plt.tight_layout()

    # 6. Xuất kết quả
    if save_path:
        # Nếu có đường dẫn, lưu thành file ảnh
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Đã lưu biểu đồ thành công tại: {save_path}")
    else:
        # Nếu không, hiển thị cửa sổ trực tiếp
        plt.show()

# --- THỰC THI KIỂM THỬ ---
if __name__ == "__main__":
    # Dữ liệu giả lập 6 tháng (Có một tháng đột biến)
    mock_history = [
        {"date": "2023-01-10", "amount": 5000000},
        {"date": "2023-02-05", "amount": 9000000}, # Tết vung tay quá trán
        {"date": "2023-03-15", "amount": 4800000},
        {"date": "2023-04-20", "amount": 4500000},
        {"date": "2023-05-10", "amount": 4200000},
        {"date": "2023-06-25", "amount": 3800000}  # Trở lại quỹ đạo tiết kiệm
    ]
    
    # Cách 1: Bật cửa sổ xem trực tiếp (Mở UI của matplotlib)
    generate_spending_trend_chart(mock_history, window_size=3)
    
    # Cách 2: Lưu ra file ảnh để gửi báo cáo (Bỏ comment dòng dưới để chạy)
    # chart_filename = "monthly_report_chart.png"
    # generate_spending_trend_chart(mock_history, window_size=3, save_path=chart_filename)