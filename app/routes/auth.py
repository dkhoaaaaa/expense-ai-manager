import re
from datetime import timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies, decode_token
from app.main import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def home():
    return render_template("landingPage.html")

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Vui lòng nhập đầy đủ email và mật khẩu!', 'warning')
            return redirect(url_for('auth.home'))
        
        from app.models.user import TaiKhoan
        user = TaiKhoan.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.mat_khau_hash, password):
            user_name = user.nguoi_dung.ho_ten if user.nguoi_dung else "Người dùng"
            
            default_avatar = f"https://ui-avatars.com/api/?name={user_name.replace(' ', '+')}&background=10b981&color=fff"
            user_avatar = user.nguoi_dung.anh_dai_dien if user.nguoi_dung and user.nguoi_dung.anh_dai_dien else default_avatar
            
            access_token = create_access_token(identity=str(user.id), additional_claims={"user_name": user_name, "user_avatar": user_avatar, "role": user.vai_tro})
            resp = redirect(url_for('auth.home'))
            set_access_cookies(resp, access_token)
            flash('Đăng nhập thành công!', 'success')
            return resp
        else:
            flash('Email hoặc mật khẩu không chính xác.', 'danger')
            return redirect(url_for('auth.home'))
    return render_template("login.html")

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not name or not email or not password or not confirm_password:
            flash('Vui lòng điền đầy đủ thông tin!', 'danger')
            return redirect(url_for('auth.home'))
            
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Định dạng email không hợp lệ!', 'danger')
            return redirect(url_for('auth.home'))
        
        if len(password) < 6:
            flash('Mật khẩu phải có ít nhất 6 ký tự!', 'danger')
            return redirect(url_for('auth.home'))
        if password != confirm_password:
            flash('Mật khẩu xác nhận không khớp!', 'danger')
            return redirect(url_for('auth.home'))
            
        from app.models.user import TaiKhoan, NguoiDung
        if TaiKhoan.query.filter_by(email=email).first():
            flash('Email đã được sử dụng, vui lòng dùng email khác!', 'danger')
            return redirect(url_for('auth.home'))
            
        try:
            hashed_pw = generate_password_hash(password)
            new_account = TaiKhoan(email=email, mat_khau_hash=hashed_pw)
            db.session.add(new_account)
            db.session.flush()
            
            new_user = NguoiDung(tai_khoan_id=new_account.id, ho_ten=name)
            db.session.add(new_user)
            db.session.commit()
            
            flash('Đăng ký thành công! Bạn có thể đăng nhập ngay bây giờ.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Lỗi khi đăng ký. Vui lòng kiểm tra lại!', 'danger')
            
        return redirect(url_for('auth.home'))
    return render_template("register.html")

@auth_bp.route('/logout')
def logout():
    resp = redirect(url_for('auth.home'))
    unset_jwt_cookies(resp)
    flash('Đã đăng xuất thành công.', 'info')
    return resp

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    email = request.form.get('email', '').strip()
    if not email:
        flash('Vui lòng nhập email!', 'warning')
        return redirect(url_for('auth.home'))
    
    from app.models.user import TaiKhoan
    account = TaiKhoan.query.filter_by(email=email).first()
    if account:
        reset_token = create_access_token(identity=str(account.id), expires_delta=timedelta(minutes=15))
        reset_link = url_for('auth.reset_password', token=reset_token, _external=True)
        flash(f'Mô phỏng gửi Email: <a href="{reset_link}" class="alert-link">Nhấn vào đây để đặt lại mật khẩu!</a>', 'info')
    else:
        flash('Nếu email hợp lệ, một liên kết khôi phục đã được gửi.', 'success')
        
    return redirect(url_for('auth.home'))

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        decoded_token = decode_token(token)
        user_id = decoded_token['sub']
    except Exception as e:
        flash('Liên kết khôi phục không hợp lệ hoặc đã hết hạn!', 'danger')
        return redirect(url_for('auth.home'))
        
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
            return redirect(url_for('auth.home'))
            
    return render_template("reset_password.html", token=token)