from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from functools import wraps
import time
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, decode_token,
    set_access_cookies, unset_jwt_cookies, get_jwt_identity, get_jwt, verify_jwt_in_request
)
import re

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
        return redirect(url_for('home'))

    # ---------------------------------------------------------
    # MIDDLEWARE BẢO VỆ ROUTE THEO QUYỀN (RBAC - Role Based Access Control)
    # ---------------------------------------------------------
    def role_required(*allowed_roles):
        def wrapper(fn):
            @wraps(fn)
            def decorator(*args, **kwargs):
                verify_jwt_in_request()
                claims = get_jwt()
                user_role = claims.get('role', 'USER')
                if user_role not in allowed_roles:
                    flash('Bạn không có quyền truy cập chức năng này!', 'danger')
                    return redirect(url_for('home'))
                return fn(*args, **kwargs)
            return decorator
        return wrapper

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
        from app.models.user import TaiKhoan, NguoiDung
        db.create_all()

    # Thêm route cơ bản trang chủ
    @app.route('/')
    def home():
        return render_template("landingPage.html")

    # Route cho trang Đăng nhập
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            
            if not email or not password:
                flash('Vui lòng nhập đầy đủ email và mật khẩu!', 'warning')
                return redirect(url_for('home'))
            
            from app.models.user import TaiKhoan
            user = TaiKhoan.query.filter_by(email=email).first()
            
            if user and check_password_hash(user.mat_khau_hash, password):
                user_name = user.nguoi_dung.ho_ten if user.nguoi_dung else "Người dùng"
                
                default_avatar = f"https://ui-avatars.com/api/?name={user_name.replace(' ', '+')}&background=10b981&color=fff"
                user_avatar = user.nguoi_dung.anh_dai_dien if user.nguoi_dung and user.nguoi_dung.anh_dai_dien else default_avatar
                
                # Tạo Access Token chứa Name, Avatar và Role
                access_token = create_access_token(identity=str(user.id), additional_claims={"user_name": user_name, "user_avatar": user_avatar, "role": user.vai_tro})
                resp = redirect(url_for('home'))
                set_access_cookies(resp, access_token)
                flash('Đăng nhập thành công!', 'success')
                return resp
            else:
                flash('Email hoặc mật khẩu không chính xác.', 'danger')
                return redirect(url_for('home'))
        return render_template("login.html")

    # Route cho trang Đăng ký
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            # 1. Kiểm tra rỗng
            if not name or not email or not password or not confirm_password:
                flash('Vui lòng điền đầy đủ thông tin!', 'danger')
                return redirect(url_for('home'))
                
            # 2. Kiểm tra định dạng Email
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                flash('Định dạng email không hợp lệ!', 'danger')
                return redirect(url_for('home'))
            
            # 3. Kiểm tra độ dài mật khẩu và khớp nhau
            if len(password) < 6:
                flash('Mật khẩu phải có ít nhất 6 ký tự!', 'danger')
                return redirect(url_for('home'))
            if password != confirm_password:
                flash('Mật khẩu xác nhận không khớp!', 'danger')
                return redirect(url_for('home'))
                
            from app.models.user import TaiKhoan, NguoiDung
            if TaiKhoan.query.filter_by(email=email).first():
                flash('Email đã được sử dụng, vui lòng dùng email khác!', 'danger')
                return redirect(url_for('home'))
                
            try:
                hashed_pw = generate_password_hash(password)
                new_account = TaiKhoan(email=email, mat_khau_hash=hashed_pw)
                db.session.add(new_account)
                db.session.flush() # Lấy ID trước khi commit
                
                new_user = NguoiDung(tai_khoan_id=new_account.id, ho_ten=name)
                db.session.add(new_user)
                db.session.commit()
                
                flash('Đăng ký thành công! Bạn có thể đăng nhập ngay bây giờ.', 'success')
            except Exception as e:
                db.session.rollback()
                flash('Lỗi khi đăng ký. Vui lòng kiểm tra lại!', 'danger')
                
            return redirect(url_for('home'))
        return render_template("register.html")
        
    # Route cho trang Hồ sơ cá nhân
    @app.route('/profile')
    @jwt_required()
    def profile():
        user_id = get_jwt_identity()
        from app.models.user import TaiKhoan
        current_user = TaiKhoan.query.get(user_id)
        return render_template("profile.html", account=current_user)

    # 1. Xử lý Cập nhật thông tin cá nhân
    @app.route('/profile/update', methods=['POST'])
    @jwt_required()
    def profile_update():
        user_id = get_jwt_identity()
        ho_ten = request.form.get('ho_ten', '').strip()
        so_dien_thoai = request.form.get('so_dien_thoai', '').strip()
        ngay_sinh = request.form.get('ngay_sinh')
        gioi_tinh = request.form.get('gioi_tinh')
        
        if not ho_ten:
            flash('Họ và tên không được để trống!', 'danger')
            return redirect(url_for('profile'))
        
        from app.models.user import NguoiDung
        user = NguoiDung.query.filter_by(tai_khoan_id=user_id).first()
        if user:
            user.ho_ten = ho_ten
            user.so_dien_thoai = so_dien_thoai
            if ngay_sinh:
                user.ngay_sinh = datetime.strptime(ngay_sinh, '%Y-%m-%d').date()
            else:
                user.ngay_sinh = None
            user.gioi_tinh = gioi_tinh
            
            db.session.commit()
            
            # Tạo lại token vì tên đã thay đổi
            access_token = create_access_token(identity=str(user_id), additional_claims={
                "user_name": ho_ten, 
                "user_avatar": get_jwt().get('user_avatar'),
                "role": get_jwt().get('role')
            })
            resp = redirect(url_for('profile'))
            set_access_cookies(resp, access_token)
            flash('Cập nhật thông tin cá nhân thành công!', 'success')
            return resp
            
        return redirect(url_for('profile'))

    # 2. Xử lý Đổi mật khẩu
    @app.route('/profile/password', methods=['POST'])
    @jwt_required()
    def profile_password():
        user_id = get_jwt_identity()
        old_password = request.form.get('old_password', '')
        new_password = request.form.get('new_password', '')
        confirm_new_password = request.form.get('confirm_new_password', '')
        
        if not old_password or not new_password or not confirm_new_password:
            flash('Vui lòng điền đầy đủ thông tin mật khẩu!', 'danger')
            return redirect(url_for('profile'))
            
        if len(new_password) < 6:
            flash('Mật khẩu mới phải có ít nhất 6 ký tự!', 'danger')
            return redirect(url_for('profile'))
        
        from app.models.user import TaiKhoan
        account = TaiKhoan.query.get(user_id)
        
        if not check_password_hash(account.mat_khau_hash, old_password):
            flash('Mật khẩu hiện tại không chính xác!', 'danger')
        elif new_password != confirm_new_password:
            flash('Mật khẩu xác nhận không khớp!', 'danger')
        else:
            account.mat_khau_hash = generate_password_hash(new_password)
            db.session.commit()
            flash('Đổi mật khẩu thành công!', 'success')
            
        return redirect(url_for('profile'))

    # 3. Xử lý Upload Avatar
    @app.route('/profile/avatar', methods=['POST'])
    @jwt_required()
    def profile_avatar():
        user_id = get_jwt_identity()
        if 'avatar' in request.files:
             file = request.files['avatar']
             if file and file.filename != '':
                 filename = secure_filename(file.filename)
                 unique_filename = f"{user_id}_{int(time.time())}_{filename}"
                 upload_folder = os.path.join('app', 'views', 'static', 'uploads', 'avatars')
                 os.makedirs(upload_folder, exist_ok=True)
                 file.save(os.path.join(upload_folder, unique_filename))
                 
                 from app.models.user import NguoiDung
                 user = NguoiDung.query.filter_by(tai_khoan_id=user_id).first()
                 if user:
                     user.anh_dai_dien = url_for('static', filename=f"uploads/avatars/{unique_filename}")
                     db.session.commit()
                     
                     access_token = create_access_token(identity=str(user_id), additional_claims={
                         "user_name": get_jwt().get('user_name'), 
                         "user_avatar": user.anh_dai_dien,
                         "role": get_jwt().get('role')
                     })
                     resp = redirect(url_for('profile'))
                     set_access_cookies(resp, access_token)
                     flash('Cập nhật ảnh đại diện thành công!', 'success')
                     return resp
        return redirect(url_for('profile'))

    # Route Đăng xuất
    @app.route('/logout')
    def logout():
        resp = redirect(url_for('home'))
        unset_jwt_cookies(resp)
        flash('Đã đăng xuất thành công.', 'info')
        return resp

    # Route xử lý Nâng cấp Premium (Demo)
    @app.route('/upgrade-premium')
    @jwt_required()
    def upgrade_premium():
        user_id = get_jwt_identity()
        from app.models.user import TaiKhoan
        account = TaiKhoan.query.get(user_id)
        
        if account.vai_tro in ['PREMIUM', 'ADMIN']:
            flash('Bạn đã là thành viên VIP rồi!', 'info')
            return redirect(url_for('home'))
            
        # Cập nhật quyền trong DB
        account.vai_tro = 'PREMIUM'
        db.session.commit()
        
        # Cập nhật lại JWT Token với role mới
        jwt_data = get_jwt()
        access_token = create_access_token(identity=str(user_id), additional_claims={
            "user_name": jwt_data.get('user_name'), 
            "user_avatar": jwt_data.get('user_avatar'),
            "role": 'PREMIUM'
        })
        resp = redirect(url_for('premium_dashboard'))
        set_access_cookies(resp, access_token)
        flash('Chúc mừng bạn đã nâng cấp Premium thành công!', 'success')
        return resp

    # Ví dụ: Route này được bảo vệ bởi Middleware (chỉ PREMIUM hoặc ADMIN mới vào được)
    @app.route('/premium-dashboard')
    @role_required('PREMIUM', 'ADMIN')
    def premium_dashboard():
        return "<h1>Chào mừng VIP! Middleware đã cho phép bạn vào trang này.</h1><br><a href='/'>Quay lại trang chủ</a>"

    # Route Xử lý Quên mật khẩu (Gửi link)
    @app.route('/forgot-password', methods=['POST'])
    def forgot_password():
        email = request.form.get('email', '').strip()
        if not email:
            flash('Vui lòng nhập email!', 'warning')
            return redirect(url_for('home'))
        
        from app.models.user import TaiKhoan
        account = TaiKhoan.query.filter_by(email=email).first()
        if account:
            # Tạo token đặc biệt để reset pass, hạn dùng 15 phút
            reset_token = create_access_token(identity=str(account.id), expires_delta=timedelta(minutes=15))
            reset_link = url_for('reset_password', token=reset_token, _external=True)
            
            # DEMO: Đưa link trực tiếp ra màn hình thay vì gửi qua Email thật
            flash(f'Mô phỏng gửi Email: <a href="{reset_link}" class="alert-link">Nhấn vào đây để đặt lại mật khẩu!</a>', 'info')
        else:
            # Vẫn báo thành công để hacker không dò được email nào tồn tại
            flash('Nếu email hợp lệ, một liên kết khôi phục đã được gửi.', 'success')
            
        return redirect(url_for('home'))

    # Route Xử lý Đặt lại mật khẩu mới
    @app.route('/reset-password/<token>', methods=['GET', 'POST'])
    def reset_password(token):
        try:
            decoded_token = decode_token(token)
            user_id = decoded_token['sub']
        except Exception as e:
            flash('Liên kết khôi phục không hợp lệ hoặc đã hết hạn!', 'danger')
            return redirect(url_for('home'))
            
        if request.method == 'POST':
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            if len(new_password) < 6:
                flash('Mật khẩu mới phải có ít nhất 6 ký tự!', 'danger')
            elif new_password != confirm_password:
                flash('Mật khẩu xác nhận không khớp!', 'danger')
            else:
                from app.models.user import TaiKhoan
                account = TaiKhoan.query.get(user_id)
                account.mat_khau_hash = generate_password_hash(new_password)
                db.session.commit()
                flash('Đặt lại mật khẩu thành công! Vui lòng đăng nhập lại.', 'success')
                return redirect(url_for('home'))
                
        return render_template("reset_password.html", token=token)

    # =========================================================
    # CỤM RESTful API DÀNH CHO MOBILE APP / FRONTEND ĐỘC LẬP
    # =========================================================
    
    # 1. API Lấy thông tin Profile
    @app.route('/api/profile', methods=['GET'])
    @jwt_required()
    def api_get_profile():
        user_id = get_jwt_identity()
        from app.models.user import TaiKhoan
        account = TaiKhoan.query.get(user_id)
        if not account:
            return jsonify({"success": False, "error": "User not found"}), 404

        user_info = account.nguoi_dung
        return jsonify({
            "success": True,
            "data": {
                "id": account.id,
                "email": account.email,
                "role": account.vai_tro,
                "name": user_info.ho_ten if user_info else None,
                "phone": user_info.so_dien_thoai if user_info else None,
                "dob": user_info.ngay_sinh.strftime('%Y-%m-%d') if user_info and user_info.ngay_sinh else None,
                "gender": user_info.gioi_tinh if user_info else None,
                "avatar": user_info.anh_dai_dien if user_info else None
            }
        }), 200

    # 2. API Cập nhật thông tin cá nhân
    @app.route('/api/profile', methods=['PUT'])
    @jwt_required()
    def api_update_profile():
        user_id = get_jwt_identity()
        data = request.json
        
        if not data or not data.get('name'):
            return jsonify({"success": False, "error": "Họ tên không được để trống"}), 400

        from app.models.user import NguoiDung
        user = NguoiDung.query.filter_by(tai_khoan_id=user_id).first()
        
        user.ho_ten = data.get('name').strip()
        user.so_dien_thoai = data.get('phone', user.so_dien_thoai)
        user.gioi_tinh = data.get('gender', user.gioi_tinh)
        
        dob_str = data.get('dob')
        if dob_str:
            try:
                user.ngay_sinh = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({"success": False, "error": "Ngày sinh sai định dạng (YYYY-MM-DD)"}), 400
        
        db.session.commit()
        return jsonify({"success": True, "message": "Cập nhật thông tin thành công"}), 200

    # 3. API Đổi mật khẩu
    @app.route('/api/profile/password', methods=['PUT'])
    @jwt_required()
    def api_change_password():
        user_id = get_jwt_identity()
        data = request.json
        
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')
        
        if not old_password or len(new_password) < 6:
            return jsonify({"success": False, "error": "Mật khẩu mới phải từ 6 ký tự"}), 400

        from app.models.user import TaiKhoan
        account = TaiKhoan.query.get(user_id)
        
        if not check_password_hash(account.mat_khau_hash, old_password):
            return jsonify({"success": False, "error": "Mật khẩu hiện tại không đúng"}), 401
            
        account.mat_khau_hash = generate_password_hash(new_password)
        db.session.commit()
        return jsonify({"success": True, "message": "Đổi mật khẩu thành công"}), 200

    # 4. API Upload Avatar
    @app.route('/api/profile/avatar', methods=['POST'])
    @jwt_required()
    def api_upload_avatar():
        user_id = get_jwt_identity()
        if 'avatar' not in request.files or request.files['avatar'].filename == '':
            return jsonify({"success": False, "error": "Vui lòng chọn file ảnh"}), 400
            
        file = request.files['avatar']
        filename = secure_filename(file.filename)
        unique_filename = f"{user_id}_{int(time.time())}_{filename}"
        upload_folder = os.path.join('app', 'views', 'static', 'uploads', 'avatars')
        os.makedirs(upload_folder, exist_ok=True)
        file.save(os.path.join(upload_folder, unique_filename))
        
        from app.models.user import NguoiDung
        user = NguoiDung.query.filter_by(tai_khoan_id=user_id).first()
        
        # _external=True để trả về URL đầy đủ (VD: http://localhost:5000/static/...)
        avatar_url = url_for('static', filename=f"uploads/avatars/{unique_filename}", _external=True)
        user.anh_dai_dien = avatar_url
        db.session.commit()
        
        return jsonify({"success": True, "message": "Upload thành công", "avatar_url": avatar_url}), 200

    # 5. API Forgot Password (Cơ bản)
    @app.route('/api/auth/forgot-password', methods=['POST'])
    def api_forgot_password():
        data = request.json
        email = data.get('email', '').strip()
        
        if not email:
            return jsonify({"success": False, "error": "Vui lòng cung cấp email"}), 400
            
        from app.models.user import TaiKhoan
        account = TaiKhoan.query.filter_by(email=email).first()
        
        # Security Best Practice: Luôn trả về 1 câu thông báo giống nhau dù email có tồn tại hay không
        # Điều này giúp hacker không dò được email nào đang có trong hệ thống
        if not account:
            return jsonify({"success": True, "message": "Nếu email hợp lệ, một liên kết khôi phục đã được gửi."}), 200
            
        # Demo Logic: Tạo ra một Reset Token giả định
        # Thực tế bạn sẽ lưu token này vào Database và gửi qua thư viện gửi Email (như Flask-Mail)
        mock_reset_token = f"reset_{account.id}_{int(time.time())}"
        
        return jsonify({
            "success": True, 
            "message": "Nếu email hợp lệ, một liên kết khôi phục đã được gửi.",
            "debug_note": "Vì chưa có cấu hình gửi Email thật, dưới đây là mã token dùng để test",
            "mock_token": mock_reset_token
        }), 200

    return app
