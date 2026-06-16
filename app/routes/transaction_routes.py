from flask import Blueprint
from app.controllers.transaction_controller import classify_transaction

# Tạo Blueprint cho phần giao dịch
transaction_bp = Blueprint('transaction_bp', __name__)

# Đăng ký route POST, gọi tới hàm classify_transaction trong controller
transaction_bp.route('/api/transactions/classify', methods=['POST'])(classify_transaction)