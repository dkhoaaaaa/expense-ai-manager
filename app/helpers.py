from functools import wraps
from flask import flash, redirect, url_for
from flask_jwt_extended import verify_jwt_in_request, get_jwt

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def role_required(*allowed_roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get('role', 'USER')
            if user_role not in allowed_roles:
                flash('Bạn không có quyền truy cập chức năng này!', 'danger')
                return redirect(url_for('auth.home'))
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def check_premium_status(account):
    from datetime import datetime
    from app import db
    if not account or not account.nguoi_dung:
        return
    user = account.nguoi_dung
    if user.is_premium and user.premium_end_date:
        if user.premium_end_date < datetime.utcnow():
            user.is_premium = False
            account.vai_tro = 'USER'
            db.session.commit()