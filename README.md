# 💸 Expense Manager AI
 
Một ứng dụng web giúp người dùng quản lý chi tiêu cá nhân, tích hợp AI tự động phân loại và dự đoán xu hướng chi tiêu, được phát triển bằng **Python (Flask)** và **Machine Learning**.
 
## 🚀 Giới thiệu
 
Expense Manager AI là một ứng dụng web giúp người dùng:
 
* 📌 Ghi lại các khoản thu/chi hằng ngày
* 🤖 Tự động phân loại chi tiêu bằng AI
* 📊 Thống kê và trực quan hóa dữ liệu tài chính
* 🔮 Dự đoán xu hướng chi tiêu trong tương lai
> 👉 **Mục tiêu:** Giúp người dùng hiểu rõ dòng tiền và quản lý tài chính hiệu quả hơn.
 
## ✨ Tính năng nổi bật
 
* **💰 Quản lý giao dịch:** Thêm / sửa / xóa giao dịch thu chi, lọc theo ngày / tháng / danh mục.
* **🤖 AI phân loại tự động:** Nhập mô tả tự nhiên (vd: *"ăn cơm tấm 35k"*) — AI tự nhận diện danh mục.
  * **Rule-based:** Phân loại theo keyword có sẵn.
  * **Machine Learning:** Naive Bayes / Logistic Regression.
* **📊 Thống kê & Báo cáo:** Tổng chi theo tháng, biểu đồ Pie chart / Bar chart, top khoản chi lớn nhất.
* **🔮 Dự đoán chi tiêu:** Dự báo tổng chi tháng tiếp theo, phát hiện xu hướng tăng/giảm.
* **⚠️ Cảnh báo overspending:** Tự động cảnh báo khi chi tiêu vượt ngưỡng.
## 🔄 Flow hoạt động
 
```
Client (Frontend)
        ↓
Route (map URL → Flask Blueprint)
        ↓
Controller (xử lý request / response)
        ↓
Service (business logic)
        ↓
Model + AI (Database + Machine Learning)
        ↓
Response trả về Client
```
 
## 🛠️ Công nghệ sử dụng
 
* **Backend:** Python, Flask, REST API.
* **Frontend:** HTML/CSS, Bootstrap, JavaScript.
* **Database:** MySQL.
* **AI / ML:** scikit-learn, pandas, numpy.
* **Kiến trúc:** MVC (Model – View – Controller).
## 📁 Cấu trúc dự án
 
```
expense-manager-ai/
├── app/
│   ├── models/                  # Model (M trong MVC)
│   │   └── transaction.py
│   ├── views/                   # View (V trong MVC)
│   │   ├── static/              # CSS, JS, images
│   │   └── templates/           # HTML (Jinja2)
│   ├── routes/                  # Routing layer
│   │   └── transaction_routes.py
│   ├── controllers/             # Controller (C trong MVC)
│   │   └── transaction_controller.py
│   ├── services/                # Business logic
│   └── ai/                      # AI / ML module
│       ├── classifier.py
│       └── predictor.py
├── database/
│   └── db.sql                   # Script MySQL
├── init.py                      # Khởi tạo Flask app
├── .env                         # Biến môi trường
├── run.py                       # Entry point
├── requirements.txt
└── README.md
```
 
## ⚙️ Hướng dẫn cài đặt và chạy dự án
 
1. **Clone repository:**
   ```bash
   git clone https://github.com/your-username/expense-manager-ai.git
   cd expense-manager-ai
   ```
 
2. **Tạo môi trường ảo:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
 
3. **Cài dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
 
4. **Setup Database:** Import file `database/db.sql` vào MySQL.
5. **Cấu hình `.env`:**
   * Tạo file `.env` ở thư mục gốc với nội dung:
   ```
   DB_USER=root
   DB_PASSWORD=123456
   DB_HOST=localhost
   DB_NAME=expense_db
   ```
 
6. **Khởi chạy ứng dụng:**
   ```bash
   python run.py
   ```
   * Mở trình duyệt và truy cập: `http://localhost:5000`