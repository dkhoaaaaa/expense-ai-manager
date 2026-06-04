import os

from app import create_app

app = create_app()

# Thêm secret_key để Flask có thể mã hóa session đăng nhập
app.secret_key = os.getenv("SECRET_KEY", "chuoi_bao_mat_mac_dinh_123")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
