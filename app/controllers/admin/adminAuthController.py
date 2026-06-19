from flask import jsonify, request
from flask_jwt_extended import create_access_token

from app.services.admin.adminAuthService import AdminAuthService


class AdminAuthController:

    @staticmethod
    def loginAdmin():
        data = request.get_json()

        if data is None:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Dữ liệu gửi lên không hợp lệ",
                    }
                ),
                400,
            )

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Vui lòng nhập đầy đủ email và mật khẩu",
                    }
                ),
                400,
            )

        result = AdminAuthService.loginAdmin(email, password)

        if not result["success"]:
            return jsonify(result), 401

        adminData = result["data"]

        accessToken = create_access_token(
            identity=str(adminData["id"]),
            additional_claims={
                "email": adminData["email"],
                "vaiTro": adminData["vaiTro"],
            },
        )

        return (
            jsonify(
                {
                    "success": True,
                    "message": result["message"],
                    "accessToken": accessToken,
                    "admin": adminData,
                }
            ),
            200,
        )
