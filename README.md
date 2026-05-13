💸 Expense Manager AI
    Web quản lý chi tiêu cá nhân tích hợp AI phân loại và dự đoán chi tiêu.

🚀 Giới thiệu:
    Expense Manager AI là một ứng dụng web giúp người dùng:
        - Ghi lại các khoản thu/chi hằng ngày
        - Tự động phân loại chi tiêu bằng AI
        - Thống kê và trực quan hóa dữ liệu tài chính
        - Dự đoán xu hướng chi tiêu trong tương lai

👉 Mục tiêu: giúp người dùng hiểu rõ dòng tiền và quản lý tài chính hiệu quả hơn.

🧠 Tính năng chính:
1. Quản lý chi tiêu
    - Thêm / sửa / xoá giao dịch
    - Phân loại: ăn uống, mua sắm, học tập...
    - Lọc theo ngày / tháng
2. AI phân loại
    - Nhập mô tả (vd: "ăn cơm tấm 35k")
    - AI tự động phân loại
    Hỗ trợ:
    - Rule-based (keyword)
    - Machine Learning (Naive Bayes / Logistic Regression)
3. Thống kê
    - Tổng chi theo tháng
    - Biểu đồ (pie chart / bar chart)
    - Top khoản chi lớn nhất
4.  Dự đoán chi tiêu
    - Dự đoán tổng chi tháng tiếp theo
    - Phát hiện xu hướng tăng/giảm
    - Cảnh báo overspending

🏗️ Công nghệ sử dụng
    Backend:
        - Python (Flask)
        - MySQL
        - REST API
    Frontend:
        - HTML / CSS (Bootstrap) / JavaScript
    AI / ML:
        - scikit-learn
        - pandas / numpy

📁 Cấu trúc project
expense-manager-ai/
│
├── app/                              # Thư mục chính chứa toàn bộ backend
│
│   ├── models/                      # (Model - M trong MVC)
│   │   └── transaction.py           # Định nghĩa bảng Transaction trong MySQL
│   │                                  (id, amount, description, category,...)
│
│   ├── views/                       # (View - V trong MVC)
│   │   ├── static/                  # File tĩnh: CSS, JS, hình ảnh
│   │   └── templates/               # HTML (render bằng Flask - Jinja2)
│   │                                  → Giao diện người dùng
│
│   ├── routes/                      # (Routing layer - tách riêng cho clean)
│   │   └── transaction_routes.py    # Định nghĩa URL (API endpoints)
│   │                                  → map URL → controller
│   │                                  → KHÔNG chứa logic xử lý
│
│   ├── controllers/                 # (Controller - C trong MVC)
│   │   └── transaction_controller.py
│   │                                  # Nhận request từ route
│   │                                  # Validate dữ liệu
│   │                                  # Gọi service xử lý
│   │                                  # Trả response (JSON)
│
│   ├── services/                    # Business logic (xử lý nghiệp vụ chính)
│   │   └── transaction_service.py
│   │                                  # Logic chính:
│   │                                  # - tạo giao dịch
│   │                                  # - gọi AI phân loại
│   │                                  # - lưu DB
│   │                                  # - dự đoán chi tiêu
│
│   ├── ai/                          # Module AI / Machine Learning
│   │   ├── classifier.py            # Phân loại chi tiêu (text → category)
│   │   └── predictor.py             # Dự đoán chi tiêu tương lai
│
│   └── __init__.py                  # Khởi tạo Flask app
│                                      # - load config
│                                      # - connect database
│                                      # - register routes
│
├── database/                        # Chứa file database
│   └── db.sql                       # Script tạo bảng MySQL
│
├── .env                             # Biến môi trường (DB_USER, DB_PASSWORD,...)
│
├── run.py                           # Entry point (chạy server Flask)
│
├── requirements.txt                 # Danh sách thư viện cần cài
│
└── README.md                        # Tài liệu project

⚙️ Cài đặt:
1. Clone repo
    git clone https://github.com/your-username/expense-manager-ai.git
    cd expense-manager-ai
2. Tạo môi trường ảo
    python -m venv venv
    venv\Scripts\activate
3. Cài dependencies
    pip install -r requirements.txt
4. Setup MySQL
    Import file:
        - database/db.sql
5. Cấu hình .env
    DB_USER=root
    DB_PASSWORD=123456
    DB_HOST=localhost
    DB_NAME=expense_db
6. Chạy project
    python run.py

👉 Truy cập: http://127.0.0.1:5000

🧠 Giải thích flow:
Client (Frontend)
    ↓
Route (map URL)
    ↓
Controller (nhận request / trả response)
    ↓
Service (xử lý logic)
    ↓
Model / AI (DB + Machine Learning)
    ↓
Response trả về client