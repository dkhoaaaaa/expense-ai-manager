from flask import Flask, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from flask_jwt_extended import (
    JWTManager, get_jwt, verify_jwt_in_request
)

db = SQLAlchemy()

# kết nối db
def create_app():
    load_dotenv()

    app = Flask(
        __name__, 
        template_folder="views/templates", 
        static_folder="views/static"
    )
    app.secret_key = os.getenv("SECRET_KEY", "super-secret-key-12345")

    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    dbname = os.getenv("DB_NAME")

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{user}:{password}@{host}/{dbname}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Cấu hình JWT
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "super-secret-jwt-key-12345")
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"] # Lưu JWT vào Cookie
    app.config["JWT_COOKIE_CSRF_PROTECT"] = False  # Tắt CSRF tạm thời để dễ test với Form HTML

    jwt = JWTManager(app)

    # Xử lý khi user chưa đăng nhập nhưng vào trang yêu cầu đăng nhập
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        flash('Vui lòng đăng nhập để truy cập.', 'warning')
        return redirect(url_for('auth.home'))

    # Đẩy dữ liệu JWT vào tất cả các template HTML thay thế cho session
    @app.context_processor
    def inject_jwt_user():
        try:
            verify_jwt_in_request(optional=True)
            jwt_data = get_jwt()
            if jwt_data:
                return {'jwt_user': {
                    'id': jwt_data.get('sub'), 
                    'name': jwt_data.get('user_name'), 
                    'avatar': jwt_data.get('user_avatar'),
                    'role': jwt_data.get('role')
                }}
        except:
            pass
        return {'jwt_user': None}

    db.init_app(app)

    with app.app_context():
        # Import model để SQLAlchemy nhận diện bảng trước khi create_all
        from app.models.taiKhoanModel import TaiKhoan
        from app.models.nguoiDungModel import NguoiDung
        db.create_all()

    from app.routes.user.auth import auth_bp
    from app.routes.user.user import user_bp
    from app.routes.user.api import api_bp
    from app.routes.admin.adminAuthRoute import adminAuthRoute
    from app.routes.user.userHomeRoute import userHomeRoute
    from app.routes.user.budget_routes import budget_bp
    from app.routes.user.category_routes import category_bp
    from app.routes.user.dashboard_routes import dashboard_bp
    from app.routes.user.transaction_routes import transaction_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(adminAuthRoute)
    app.register_blueprint(userHomeRoute)
    app.register_blueprint(budget_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transaction_bp)

    return app
