import os
import time
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, create_access_token, set_access_cookies
from app import db
from app.helpers import allowed_file, role_required
from sqlalchemy import text

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile')
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    from app.models.taiKhoanModel import TaiKhoan
    current_user = TaiKhoan.query.get(user_id)
    
    from app.helpers import check_premium_status
    check_premium_status(current_user)
    
    return render_template("user/profile.html", account=current_user)

@user_bp.route('/ai-assistant')
@jwt_required()
def ai_assistant():
    return render_template("user/index.html")

@user_bp.route('/api/analytics/forecast', methods=['GET'])
@jwt_required()
def api_forecast_expense():
    user_id = get_jwt_identity()
    try:
        # Lấy tất cả giao dịch chi tiêu của user
        transactions_db = db.session.execute(
            text("""
                SELECT gd.ngay_giao_dich, gd.so_tien
                FROM giao_dich gd
                WHERE gd.tai_khoan_id = :userId AND gd.loai = 'CHI'
                ORDER BY gd.ngay_giao_dich ASC
            """),
            {"userId": user_id}
        ).fetchall()
        
        formatted_transactions = [
            {"date": str(row[0]), "amount": float(row[1])}
            for row in transactions_db
        ]
        
        from app.ai.predictor import ExpensePredictor
        predictor = ExpensePredictor()
        result = predictor.forecast_next_month(formatted_transactions)
        
        if result.get('status') == 'error':
            return jsonify(result), 400
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@user_bp.route('/api/analytics/trend/mom', methods=['GET'])
@jwt_required()
def api_mom_trend():
    user_id = get_jwt_identity()
    try:
        transactions_db = db.session.execute(
            text("""
                SELECT gd.ngay_giao_dich, gd.so_tien, dm.ten_danh_muc
                FROM giao_dich gd
                LEFT JOIN danh_muc dm ON gd.danh_muc_id = dm.id
                WHERE gd.tai_khoan_id = :userId AND gd.loai = 'CHI'
                ORDER BY gd.ngay_giao_dich ASC
            """),
            {"userId": user_id}
        ).fetchall()
        
        formatted_transactions = [
            {"date": str(row[0]), "amount": float(row[1]), "category": row[2] or "Khác"}
            for row in transactions_db
        ]
        
        from app.ai.analytics import ExpenseAnalyzer
        analyzer = ExpenseAnalyzer()
        result = analyzer.analyze_spending_trends(formatted_transactions)
        
        if result.get('status') == 'error':
            return jsonify(result), 400
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@user_bp.route('/api/analytics/trend/timeseries', methods=['GET'])
@jwt_required()
def api_timeseries_trend():
    user_id = get_jwt_identity()
    try:
        window_size = int(request.args.get('window_size', 3))
        transactions_db = db.session.execute(
            text("""
                SELECT gd.ngay_giao_dich, gd.so_tien
                FROM giao_dich gd
                WHERE gd.tai_khoan_id = :userId AND gd.loai = 'CHI'
                ORDER BY gd.ngay_giao_dich ASC
            """),
            {"userId": user_id}
        ).fetchall()
        
        formatted_transactions = [
            {"date": str(row[0]), "amount": float(row[1])}
            for row in transactions_db
        ]
        
        from app.ai.analytics import ExpenseAnalyzer
        analyzer = ExpenseAnalyzer()
        result = analyzer.analyze_time_series_trend(formatted_transactions, window_size=window_size)
        
        if result.get('status') == 'error':
            return jsonify(result), 400
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@user_bp.route('/profile/update', methods=['POST'])
@jwt_required()
def profile_update():
    user_id = get_jwt_identity()
    ho_ten = request.form.get('ho_ten', '').strip()
    so_dien_thoai = request.form.get('so_dien_thoai', '').strip()
    ngay_sinh = request.form.get('ngay_sinh')
    gioi_tinh = request.form.get('gioi_tinh')
    
    if not ho_ten:
        flash('Họ và tên không được để trống!', 'danger')
        return redirect(url_for('user.profile'))
    
    from app.models.nguoiDungModel import NguoiDung
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
        
        access_token = create_access_token(identity=str(user_id), additional_claims={
            "user_name": ho_ten, 
            "user_avatar": get_jwt().get('user_avatar'),
            "role": get_jwt().get('role')
        })
        resp = redirect(url_for('user.profile'))
        set_access_cookies(resp, access_token)
        flash('Cập nhật thông tin cá nhân thành công!', 'success')
        return resp
        
    return redirect(url_for('user.profile'))

@user_bp.route('/profile/password', methods=['POST'])
@jwt_required()
def profile_password():
    user_id = get_jwt_identity()
    old_password = request.form.get('old_password', '')
    new_password = request.form.get('new_password', '')
    confirm_new_password = request.form.get('confirm_new_password', '')
    
    if not old_password or not new_password or not confirm_new_password:
        flash('Vui lòng điền đầy đủ thông tin mật khẩu!', 'danger')
        return redirect(url_for('user.profile'))
        
    if len(new_password) < 6:
        flash('Mật khẩu mới phải có ít nhất 6 ký tự!', 'danger')
        return redirect(url_for('user.profile'))
    
    from app.models.taiKhoanModel import TaiKhoan
    account = TaiKhoan.query.get(user_id)
    
    if not check_password_hash(account.mat_khau_hash, old_password):
        flash('Mật khẩu hiện tại không chính xác!', 'danger')
    elif new_password != confirm_new_password:
        flash('Mật khẩu xác nhận không khớp!', 'danger')
    else:
        account.mat_khau_hash = generate_password_hash(new_password)
        db.session.commit()
        flash('Đổi mật khẩu thành công!', 'success')
        
    return redirect(url_for('user.profile'))

@user_bp.route('/profile/avatar', methods=['POST'])
@jwt_required()
def profile_avatar():
    user_id = get_jwt_identity()
    if 'avatar' in request.files:
        file = request.files['avatar']
        if file and file.filename != '':
            if not allowed_file(file.filename):
                flash('Chỉ hỗ trợ upload định dạng ảnh hợp lệ (PNG, JPG, GIF)!', 'danger')
                return redirect(url_for('user.profile'))

            filename = secure_filename(file.filename)
            unique_filename = f"{user_id}_{int(time.time())}_{filename}"
            upload_folder = os.path.join('app', 'views', 'static', 'uploads', 'avatars')
            os.makedirs(upload_folder, exist_ok=True)
            file.save(os.path.join(upload_folder, unique_filename))
            
            from app.models.nguoiDungModel import NguoiDung
            user = NguoiDung.query.filter_by(tai_khoan_id=user_id).first()
            if user:
                user.anh_dai_dien = url_for('static', filename=f"uploads/avatars/{unique_filename}")
                db.session.commit()
                
                access_token = create_access_token(identity=str(user_id), additional_claims={
                    "user_name": get_jwt().get('user_name'), 
                    "user_avatar": user.anh_dai_dien,
                    "role": get_jwt().get('role')
                })
                resp = redirect(url_for('user.profile'))
                set_access_cookies(resp, access_token)
                flash('Cập nhật ảnh đại diện thành công!', 'success')
                return resp
    return redirect(url_for('user.profile'))

@user_bp.route('/upgrade-premium')
@jwt_required()
def upgrade_premium():
    user_id = get_jwt_identity()
    from app.models.taiKhoanModel import TaiKhoan
    account = TaiKhoan.query.get(user_id)
    
    if account.vai_tro in ['PREMIUM', 'ADMIN']:
        flash('Bạn đã là thành viên VIP rồi!', 'info')
        return redirect(url_for('auth.home'))
        
    account.vai_tro = 'PREMIUM'
    db.session.commit()
    
    jwt_data = get_jwt()
    access_token = create_access_token(identity=str(user_id), additional_claims={
        "user_name": jwt_data.get('user_name'), 
        "user_avatar": jwt_data.get('user_avatar'),
        "role": 'PREMIUM'
    })
    resp = redirect(url_for('user.premium_dashboard'))
    set_access_cookies(resp, access_token)
    flash('Chúc mừng bạn đã nâng cấp Premium thành công!', 'success')
    return resp

@user_bp.route('/premium-dashboard')
@role_required('PREMIUM', 'ADMIN')
def premium_dashboard():
    return "<h1>Chào mừng VIP! Middleware đã cho phép bạn vào trang này.</h1><br><a href='/'>Quay lại trang chủ</a>"

@user_bp.route('/premium')
@jwt_required()
def premium_page():
    return render_template("user/premium.html")

@user_bp.route('/premium/payment')
@jwt_required()
def premium_payment_page():
    return render_template("user/payment.html")