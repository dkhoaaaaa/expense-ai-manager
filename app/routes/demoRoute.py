import os
import random
import re
import jwt
import datetime
from functools import wraps
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, current_app

demo_bp = Blueprint("demo", __name__)

# Tạo một biến toàn cục (dictionary) để giả lập CSDL lưu trên RAM
mock_db = {}

JWT_SECRET = "super_secret_jwt_key_ai_expense"

@demo_bp.before_request
def verify_jwt_cookie():
    token = request.cookies.get('jwt_token')
    if token:
        try:
            data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            email_or_phone = data['sub']
            
            found_user = None
            for user_data in mock_db.values():
                if (user_data.get('email') == email_or_phone and user_data.get('email') != 'Chưa cập nhật') or \
                   (user_data.get('so_dien_thoai') == email_or_phone and user_data.get('so_dien_thoai') != 'Chưa cập nhật'):
                    found_user = user_data
                    break
            
            if found_user:
                session['user'] = found_user
            else:
                session.pop('user', None)
        except Exception:
            session.pop('user', None)
    else:
        session.pop('user', None)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user'):
            if request.path.startswith('/api/'):
                return jsonify({"success": False, "message": "Vui lòng đăng nhập để tiếp tục!"}), 401
            return redirect(url_for('demo.home'))
        return f(*args, **kwargs)
    return decorated_function

def validate_email_phone(email_or_phone):
    if '@' in email_or_phone:
        if not re.match(r"^[^\s@]+@gmail\.com$", email_or_phone):
            return "Email phải có định dạng @gmail.com!"
    else:
        if not re.match(r"^0\d{9}$", email_or_phone):
            return "Số điện thoại phải bắt đầu bằng 0 và có đúng 10 chữ số!"
    return None

def validate_password(password):
    if len(password) < 6:
        return "Mật khẩu phải có ít nhất 6 ký tự!"
    if not re.match(r"^[a-zA-Z0-9]+$", password):
        return "Mật khẩu không được chứa ký tự đặc biệt!"
    return None


@demo_bp.route("/")
def home():
    return render_template("landingPage.html")


@demo_bp.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        # Giả lập lấy tên từ email (phần trước chữ @) do chưa kết nối Database
        email_or_phone = request.form.get("email", "")
        password = request.form.get("password", "")
        
        # Nâng cấp: Tìm user bằng email hoặc SĐT thay vì chỉ tìm bằng key
        found_user_data = None
        for user_data in mock_db.values():
            if (user_data.get('email') == email_or_phone and user_data.get('email') != 'Chưa cập nhật') or \
               (user_data.get('so_dien_thoai') == email_or_phone and user_data.get('so_dien_thoai') != 'Chưa cập nhật'):
                found_user_data = user_data
                break

        if found_user_data:
            if found_user_data.get('password') and found_user_data.get('password') != password:
                return render_template("login.html", mode="login", message="Tài khoản hoặc mật khẩu không chính xác!")
            session['user'] = found_user_data
        else:
            is_email = '@' in email_or_phone
            new_user = {
                'ho_ten': 'Chưa cập nhật', 
                'email': email_or_phone if is_email else 'Chưa cập nhật',
                'so_dien_thoai': email_or_phone if not is_email else 'Chưa cập nhật',
                'gioi_tinh': 'Chưa cập nhật',
                'ngay_sinh': 'Chưa cập nhật',
                'cccd': 'Chưa cập nhật',
                'anh_dai_dien': None,
                'password': password
            }
            mock_db[email_or_phone] = new_user
            session['user'] = new_user
        return redirect(url_for('demo.home'))
            
    return render_template("login.html", mode="login", message=None)


@demo_bp.route("/logout")
def logout():
    # Xóa thông tin user khỏi session khi nhấn nút Đăng xuất
    session.pop('user', None)
    resp = redirect(url_for('demo.home'))
    resp.delete_cookie('jwt_token')
    return resp


@demo_bp.route("/register", methods=["GET"])
def register_page():
    return render_template("login.html", mode="register", message=None)


@demo_bp.route("/api/register", methods=["POST"])
def api_register():
    data = request.json
    fullname = data.get("fullname")
    email_or_phone = data.get("email", "")
    password = data.get("password", "")
    
    err = validate_email_phone(email_or_phone) or validate_password(password)
    if err:
        return jsonify({"success": False, "message": err})

    # Kiểm tra xem đã tồn tại chưa
    for user_data in mock_db.values():
        if (user_data.get('email') == email_or_phone and user_data.get('email') != 'Chưa cập nhật') or \
           (user_data.get('so_dien_thoai') == email_or_phone and user_data.get('so_dien_thoai') != 'Chưa cập nhật'):
            return jsonify({"success": False, "message": "Tài khoản này đã được đăng ký!"})

    is_email = '@' in email_or_phone
    new_user = {
        'ho_ten': fullname, 'email': email_or_phone if is_email else 'Chưa cập nhật',
        'so_dien_thoai': email_or_phone if not is_email else 'Chưa cập nhật',
        'gioi_tinh': 'Chưa cập nhật', 'ngay_sinh': 'Chưa cập nhật', 'cccd': 'Chưa cập nhật',
        'anh_dai_dien': None, 'password': generate_password_hash(password)
    }
    mock_db[email_or_phone] = new_user
    
    token = jwt.encode({
        'sub': email_or_phone,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, JWT_SECRET, algorithm='HS256')
    resp = jsonify({"success": True})
    resp.set_cookie('jwt_token', token, httponly=True)
    return resp

@demo_bp.route("/update-profile", methods=["POST"])
@login_required
def update_profile():
    user_data = session['user'].copy()
    user_data['ho_ten'] = request.form.get('ho_ten') or 'Chưa cập nhật'
    user_data['gioi_tinh'] = request.form.get('gioi_tinh') or 'Chưa cập nhật'
    user_data['ngay_sinh'] = request.form.get('ngay_sinh') or 'Chưa cập nhật'
    user_data['so_dien_thoai'] = request.form.get('so_dien_thoai') or 'Chưa cập nhật'
    user_data['cccd'] = request.form.get('cccd') or 'Chưa cập nhật'
    
    if 'anh_dai_dien' in request.files:
        file = request.files['anh_dai_dien']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(current_app.static_folder, "uploads")
            os.makedirs(upload_folder, exist_ok=True)
            file.save(os.path.join(upload_folder, filename))
            user_data['anh_dai_dien'] = f"uploads/{filename}"
            
    session['user'] = user_data
    
    # Lưu lại vào DB giả lập để không mất dữ liệu khi đăng xuất
    email = user_data.get('email')
    phone = user_data.get('so_dien_thoai')
    
    orig_key = None
    for key, u in mock_db.items():
        if (u.get('email') == email and email != 'Chưa cập nhật') or \
           (u.get('so_dien_thoai') == phone and phone != 'Chưa cập nhật'):
            orig_key = key
            break
            
    if orig_key:
        user_data['password'] = mock_db[orig_key].get('password')
        mock_db[orig_key] = user_data
    else:
        mock_db[email if email != 'Chưa cập nhật' else phone] = user_data
            
    return redirect(url_for('demo.home'))


@demo_bp.route("/api/change-password", methods=["POST"])
@login_required
def api_change_password():
    data = request.json
    current_password = data.get("current_password")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_new_password")
    
    err = validate_password(new_password)
    if err:
        return jsonify({"success": False, "message": err})

    if new_password != confirm_password:
        return jsonify({"success": False, "message": "Mật khẩu mới không khớp!"})
    
    email = session['user'].get('email')
    phone = session['user'].get('so_dien_thoai')
    
    orig_key = None
    for key, u in mock_db.items():
        if (u.get('email') == email and email != 'Chưa cập nhật') or \
           (u.get('so_dien_thoai') == phone and phone != 'Chưa cập nhật'):
            orig_key = key
            break
            
    if orig_key:
        if mock_db[orig_key].get('password') and check_password_hash(mock_db[orig_key].get('password'), current_password):
            hashed_pw = generate_password_hash(new_password)
            mock_db[orig_key]['password'] = hashed_pw
            session['user']['password'] = hashed_pw
            session.modified = True
            return jsonify({"success": True, "message": "Bạn đã đổi mật khẩu thành công!"})
        else:
            return jsonify({"success": False, "message": "Mật khẩu hiện tại không đúng!"})
            
    return jsonify({"success": False, "message": "Lỗi hệ thống!"})


@demo_bp.route("/api/forgot-password", methods=["POST"])
def forgot_password_api():
    data = request.json
    email_or_phone = data.get("email")
    
    otp = str(random.randint(100000, 999999))
    session['reset_email'] = email_or_phone
    session['reset_otp'] = otp
    
    return jsonify({"success": True, "otp": otp})


@demo_bp.route("/api/login", methods=["POST"])
def api_login():
    data = request.json
    email_or_phone = data.get("email", "")
    password = data.get("password", "")

    err = validate_email_phone(email_or_phone) or validate_password(password)
    if err:
        return jsonify({"success": False, "message": err})

    # Nâng cấp: Tìm user bằng email hoặc SĐT thay vì chỉ tìm bằng key
    found_user_data = None
    for user_data in mock_db.values():
        if (user_data.get('email') == email_or_phone and user_data.get('email') != 'Chưa cập nhật') or \
           (user_data.get('so_dien_thoai') == email_or_phone and user_data.get('so_dien_thoai') != 'Chưa cập nhật'):
            found_user_data = user_data
            break

    if found_user_data:
        if found_user_data.get('password') and not check_password_hash(found_user_data.get('password'), password):
            return jsonify({"success": False, "message": "Sai mật khẩu!"})
    else:
        is_email = '@' in email_or_phone
        new_user = {
            'ho_ten': 'Chưa cập nhật', 
            'email': email_or_phone if is_email else 'Chưa cập nhật',
            'so_dien_thoai': email_or_phone if not is_email else 'Chưa cập nhật', 'gioi_tinh': 'Chưa cập nhật', 'ngay_sinh': 'Chưa cập nhật', 'cccd': 'Chưa cập nhật', 'anh_dai_dien': None, 'password': generate_password_hash(password) }
        mock_db[email_or_phone] = new_user
        
    token = jwt.encode({
        'sub': email_or_phone,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, JWT_SECRET, algorithm='HS256')
    resp = jsonify({"success": True})
    resp.set_cookie('jwt_token', token, httponly=True)
    return resp


@demo_bp.route("/api/verify-otp", methods=["POST"])
def verify_otp_api():
    data = request.json
    email = data.get("email")
    otp = data.get("otp")
    
    saved_email = session.get('reset_email')
    saved_otp = session.get('reset_otp')

    if saved_email and saved_email == email and saved_otp == otp:
        session['otp_verified'] = True
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Invalid OTP"})


@demo_bp.route("/api/reset-password", methods=["POST"])
def api_reset_password():
    data = request.json
    email = data.get("email")
    new_pw = data.get("new_password")
    confirm_pw = data.get("confirm_password")
    
    err = validate_password(new_pw)
    if err:
        return jsonify({"success": False, "message": err})

    saved_email = session.get('reset_email')
    otp_verified = session.get('otp_verified')

    if not saved_email or not otp_verified or email != saved_email:
        return jsonify({"success": False, "message": "Phiên làm việc không hợp lệ!"})
            
    if new_pw != confirm_pw:
        return jsonify({"success": False, "message": "Mật khẩu mới không khớp!"})

    # Cập nhật mật khẩu mới vào cơ sở dữ liệu giả lập
    orig_key = None
    for key, u in mock_db.items():
        if (u.get('email') == email and email != 'Chưa cập nhật') or \
           (u.get('so_dien_thoai') == email and email != 'Chưa cập nhật'):
            orig_key = key
            break
    if orig_key:
        mock_db[orig_key]['password'] = generate_password_hash(new_pw)

    # Xóa thông tin OTP khỏi session sau khi đổi thành công
    session.pop('reset_email', None)
    session.pop('reset_otp', None)
    session.pop('otp_verified', None)
    
    return jsonify({"success": True, "message": "Bạn đã đổi mật khẩu thành công!"})


@demo_bp.route("/transactions/add", methods=["POST"])
@login_required
def add_transaction():
    data = request.json
    amount = data.get("amount")
    description = data.get("description")

    # fake AI
    if "ăn" in description.lower():
        category = "Ăn uống"
    elif "xăng" in description.lower():
        category = "Di chuyển"
    else:
        category = "Khác"

    return jsonify({"id": 1, "category": category})
