from flask import jsonify, request
from app.services.user.userHomeService import UserHomeService
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request


class UserHomeController:

    @staticmethod
    def getHomeData():
        # Lấy user_id tự động từ JWT token, nếu không có/không hợp lệ thì lấy từ query parameter (mặc định là 2)
        userId = 2
        try:
            verify_jwt_in_request(optional=True)
            jwt_user_id = get_jwt_identity()
            if jwt_user_id:
                userId = int(jwt_user_id)
            else:
                userIdStr = request.args.get("user_id")
                if userIdStr:
                    userId = int(userIdStr)
        except Exception:
            userIdStr = request.args.get("user_id")
            try:
                if userIdStr:
                    userId = int(userIdStr)
            except ValueError:
                userId = 2
            
        data = UserHomeService.getHomeData(userId)
        
        return jsonify({
            "success": True,
            "data": data
        }), 200
