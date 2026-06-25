import os
import time
from datetime import datetime
from flask import Blueprint, request, jsonify, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.helpers import allowed_file
import google.generativeai as genai

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/profile', methods=['GET'])
@jwt_required()
def api_get_profile():
    user_id = get_jwt_identity()
    from app.models.taiKhoanModel import TaiKhoan
    account = TaiKhoan.query.get(user_id)
    if not account:
        return jsonify({"success": False, "error": "User not found"}), 404

    from app.helpers import check_premium_status
    check_premium_status(account)

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

@api_bp.route('/profile', methods=['PUT'])
@jwt_required()
def api_update_profile():
    user_id = get_jwt_identity()
    data = request.json
    
    if not data or not data.get('name'):
        return jsonify({"success": False, "error": "Họ tên không được để trống"}), 400

    from app.models.nguoiDungModel import NguoiDung
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

@api_bp.route('/profile/password', methods=['PUT'])
@jwt_required()
def api_change_password():
    user_id = get_jwt_identity()
    data = request.json
    
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')
    
    if not old_password or len(new_password) < 6:
        return jsonify({"success": False, "error": "Mật khẩu mới phải từ 6 ký tự"}), 400

    from app.models.taiKhoanModel import TaiKhoan
    account = TaiKhoan.query.get(user_id)
    
    if not check_password_hash(account.mat_khau_hash, old_password):
        return jsonify({"success": False, "error": "Mật khẩu hiện tại không đúng"}), 401
        
    account.mat_khau_hash = generate_password_hash(new_password)
    db.session.commit()
    return jsonify({"success": True, "message": "Đổi mật khẩu thành công"}), 200

@api_bp.route('/profile/avatar', methods=['POST'])
@jwt_required()
def api_upload_avatar():
    user_id = get_jwt_identity()
    if 'avatar' not in request.files or request.files['avatar'].filename == '':
        return jsonify({"success": False, "error": "Vui lòng chọn file ảnh"}), 400
        
    file = request.files['avatar']
    if not allowed_file(file.filename):
        return jsonify({"success": False, "error": "Định dạng file không hỗ trợ"}), 400

    filename = secure_filename(file.filename)
    unique_filename = f"{user_id}_{int(time.time())}_{filename}"
    upload_folder = os.path.join('app', 'views', 'static', 'uploads', 'avatars')
    os.makedirs(upload_folder, exist_ok=True)
    file.save(os.path.join(upload_folder, unique_filename))
    
    from app.models.nguoiDungModel import NguoiDung
    user = NguoiDung.query.filter_by(tai_khoan_id=user_id).first()
    
    avatar_url = url_for('static', filename=f"uploads/avatars/{unique_filename}", _external=True)
    user.anh_dai_dien = avatar_url
    db.session.commit()
    
    return jsonify({"success": True, "message": "Upload thành công", "avatar_url": avatar_url}), 200

@api_bp.route('/auth/forgot-password', methods=['POST'])
def api_forgot_password():
    data = request.json
    email = data.get('email', '').strip()
    
    if not email:
        return jsonify({"success": False, "error": "Vui lòng cung cấp email"}), 400
        
    from app.models.taiKhoanModel import TaiKhoan
    account = TaiKhoan.query.filter_by(email=email).first()
    
    if not account:
        return jsonify({"success": True, "message": "Nếu email hợp lệ, một liên kết khôi phục đã được gửi."}), 200
        
    mock_reset_token = f"reset_{account.id}_{int(time.time())}"
    
    return jsonify({
        "success": True, 
        "message": "Nếu email hợp lệ, một liên kết khôi phục đã được gửi.",
        "debug_note": "Vì chưa có cấu hình gửi Email thật, dưới đây là mã token dùng để test",
        "mock_token": mock_reset_token
    }), 200

@api_bp.route('/premium/activate', methods=['POST'])
@jwt_required()
def api_activate_premium():
    from datetime import datetime, timedelta
    from flask_jwt_extended import create_access_token, set_access_cookies, get_jwt
    user_id = get_jwt_identity()
    
    from app.models.nguoiDungModel import NguoiDung
    from app.models.taiKhoanModel import TaiKhoan
    
    user = NguoiDung.query.filter_by(tai_khoan_id=user_id).first()
    account = TaiKhoan.query.get(user_id)
    
    if not user or not account:
        return jsonify({"success": False, "error": "Người dùng không tồn tại"}), 404
        
    data = request.json or {}
    payment_method = data.get('payment_method', 'BANKING').upper()
    
    from app.models.goiPremiumModel import GoiPremium
    from app.models.thanhToanModel import ThanhToan
    
    user.is_premium = True
    user.premium_start_date = datetime.utcnow()
    user.premium_end_date = datetime.utcnow() + timedelta(days=30)
    
    # Cập nhật vai trò tài khoản để đồng bộ hóa phân quyền
    account.vai_tro = 'PREMIUM'
    
    # Tạo bản ghi Gói Premium mới
    new_goi = GoiPremium(
        idTK=int(user_id),
        tenGoi="PREMIUM",
        gia=49000.00,
        trangThai="ACTIVE",
        ngayBatDau=datetime.utcnow(),
        ngayKetThuc=datetime.utcnow() + timedelta(days=30),
        ngayTao=datetime.utcnow()
    )
    db.session.add(new_goi)
    db.session.flush() # Để sinh ID của gói premium cho khóa ngoại của bảng thanh_toan
    
    # Tạo bản ghi Ghi nhận Thanh toán mới
    new_payment = ThanhToan(
        idTK=int(user_id),
        idGoiPremium=new_goi.id,
        soTien=49000.00,
        phuongThucThanhToan=payment_method,
        trangThaiThanhToan="SUCCESS",
        maGiaoDich=f"TXN{int(time.time())}{user_id}",
        ngayThanhToan=datetime.utcnow(),
        ngayTao=datetime.utcnow()
    )
    db.session.add(new_payment)
    
    db.session.commit()
    
    # Tạo lại access token mới có chứa role = 'PREMIUM' và set cookie
    jwt_data = get_jwt()
    current_avatar = jwt_data.get('user_avatar') if jwt_data else None
    if not current_avatar:
        current_avatar = user.anh_dai_dien or f"https://ui-avatars.com/api/?name={user.ho_ten.replace(' ', '+')}&background=10b981&color=fff"

    access_token = create_access_token(identity=str(user_id), additional_claims={
        "user_name": user.ho_ten, 
        "user_avatar": current_avatar,
        "role": 'PREMIUM'
    })
    
    response = jsonify({
        "success": True,
        "message": "Kích hoạt Premium thành công"
    })
    set_access_cookies(response, access_token)
    return response, 200

@api_bp.route('/ai/chat', methods=['POST'])
@jwt_required()
def api_chat():
    user_id = get_jwt_identity()
    data = request.json or {}
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({"success": False, "error": "Vui lòng cung cấp nội dung chat"}), 400
        
    try:
        # 1. Xác thực và kiểm tra trạng thái Premium trong database
        from app.models.taiKhoanModel import TaiKhoan
        from app.models.tinNhanChatbotModel import TinNhanChatbot
        account = TaiKhoan.query.get(user_id)
        if not account:
            return jsonify({"success": False, "error": "Người dùng không tồn tại"}), 404
            
        # Kiểm tra và tự động cập nhật thời hạn Premium
        from app.helpers import check_premium_status
        check_premium_status(account)
        
        # Chặn nếu không phải Premium hoặc Admin
        if account.vai_tro not in ['PREMIUM', 'ADMIN']:
            return jsonify({
                "success": False, 
                "error": "Tính năng Chatbot AI chỉ dành riêng cho tài khoản Premium."
            }), 403
            
        # Lưu tin nhắn của User vào DB trước khi gọi AI
        user_msg = TinNhanChatbot(
            idTK=user_id,
            nguoiGui='USER',
            noiDung=message,
            ngayTao=datetime.utcnow()
        )
        db.session.add(user_msg)
        db.session.commit()
            
        # 2. Gọi AI Service để sinh câu trả lời
        from app.services.ai.ai_service import AIService
        reply = AIService.generate_response(user_id, message)
        
        # Lưu tin nhắn của Bot vào DB sau khi sinh câu trả lời thành công
        bot_msg = TinNhanChatbot(
            idTK=user_id,
            nguoiGui='BOT',
            noiDung=reply,
            ngayTao=datetime.utcnow()
        )
        db.session.add(bot_msg)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "reply": reply
        }), 200
        
    except ValueError as ve:
        # Bắt lỗi cấu hình (thiếu API Key)
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        # Bắt các lỗi kết nối hoặc lỗi bất ngờ khác
        return jsonify({"success": False, "error": f"Lỗi chatbot: {str(e)}"}), 500

@api_bp.route('/ai/chat/history', methods=['GET'])
@jwt_required()
def api_chat_history():
    user_id = get_jwt_identity()
    try:
        from app.models.tinNhanChatbotModel import TinNhanChatbot
        from app.models.taiKhoanModel import TaiKhoan
        account = TaiKhoan.query.get(user_id)
        if not account:
            return jsonify({"success": False, "error": "Người dùng không tồn tại"}), 404
            
        # Kiểm tra và tự động cập nhật thời hạn Premium
        from app.helpers import check_premium_status
        check_premium_status(account)
        
        # Chặn nếu không phải Premium hoặc Admin
        if account.vai_tro not in ['PREMIUM', 'ADMIN']:
            return jsonify({
                "success": False, 
                "error": "Tính năng Chatbot AI chỉ dành riêng cho tài khoản Premium."
            }), 403

        # Lấy tối đa 3 tin nhắn gần đây nhất từ DB (mới nhất xếp trước)
        history = TinNhanChatbot.query.filter_by(idTK=user_id)\
            .order_by(TinNhanChatbot.id.desc())\
            .limit(3)\
            .all()
            
        # Đảo ngược mảng để sắp xếp từ cũ đến mới (để hiện đúng luồng chat)
        history.reverse()
        
        messages_data = []
        for msg in history:
            messages_data.append({
                "sender": "user" if msg.nguoiGui == "USER" else "bot",
                "text": msg.noiDung
            })
            
        return jsonify({
            "success": True,
            "messages": messages_data
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": f"Lỗi lấy lịch sử chatbot: {str(e)}"}), 500
