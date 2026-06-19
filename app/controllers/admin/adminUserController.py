import os
from math import e

from flask import jsonify, request
from flask_jwt_extended import get_jwt
from werkzeug.utils import secure_filename
import uuid

from app.services.admin.adminUserService import AdminUserService


class AdminUserController:

    @staticmethod
    def getAdminProfile():
        try:
            claims = get_jwt()
            email = claims.get("email")

            if not email:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Không tìm thấy thông tin email trong token",
                        }
                    ),
                    400,
                )

            result = AdminUserService.getAdminUser(email)
            if not result["success"]:
                return jsonify(result), 404

            return jsonify(result), 200
        except Exception as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Lỗi lấy thông tin admin: {str(e)}",
                    }
                ),
                500,
            )

    @staticmethod
    def updateAdminProfile():
        try:
            claims = get_jwt()
            email = claims.get("email")
            if not email:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Không tìm thấy thông tin admin trong token",
                        }
                    ),
                    400,
                )
            result = AdminUserService.updateAdminUser(email)
            if not result["success"]:
                return jsonify(result), 400
            return jsonify(result), 200
        except Exception as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Lỗi cập nhật thông tin admin: {str(e)}",
                    }
                ),
                500,
            )

    @staticmethod
    def changePassword():
        claims = get_jwt()
        email = claims.get("email")

        if not email:
            return jsonify({"success": False, "message": "Dữ liệu không hợp lệ"}), 400

        data = request.get_json() or {}

        result = AdminUserService.changePassword(
            email=email,
            currentPassword=data.get("currentPassword"),
            newPassword=data.get("newPassword"),
            confirmPassword=data.get("confirmPassword"),
        )

        statusCode = 200 if result["success"] else 400
        return jsonify(result), statusCode

    @staticmethod
    def uploadAvatar():
        try:
            claims = get_jwt()
            email = claims.get("email")

            if not email:
                return jsonify({
                    "success": False,
                    "message": "Không tìm thấy thông tin admin trong token"
                }), 400

            if "avatar" not in request.files:
                return jsonify({
                    "success": False,
                    "message": "Không tìm thấy file upload"
                }), 400

            file = request.files["avatar"]

            if file.filename == "":
                return jsonify({
                    "success": False,
                    "message": "Chưa chọn file"
                }), 400

            allowedExtensions = {"png", "jpg", "jpeg", "gif"}
            filename = file.filename
            ext = filename.rsplit(".", 1)[1].lower() if "." in filename else ""

            if ext not in allowedExtensions:
                return jsonify({
                    "success": False,
                    "message": "Định dạng file không hợp lệ. Chỉ cho phép png, jpg, jpeg, gif"
                }), 400

            file.seek(0, os.SEEK_END)
            fileSize = file.tell()
            file.seek(0)

            if fileSize > 2 * 1024 * 1024:
                return jsonify({
                    "success": False,
                    "message": "Dung lượng file vượt quá 2MB"
                }), 400

            # Lấy avatar cũ trước khi update
            oldAvatar = AdminUserService.getCurrentAvatar(email)

            # Đường dẫn tới thư mục static
            staticDir = os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(os.path.abspath(__file__))
                    )
                ),
                "views",
                "static"
            )

            uploadSubpath = os.path.join("img", "admin")
            uploadDir = os.path.join(staticDir, uploadSubpath)
            os.makedirs(uploadDir, exist_ok=True)

            uniqueFilename = f"{uuid.uuid4().hex}_{secure_filename(filename)}"
            filePath = os.path.join(uploadDir, uniqueFilename)

            # Lưu file mới
            file.save(filePath)

            avatarWebPath = f"/static/img/admin/{uniqueFilename}"

            # Cập nhật DB
            result = AdminUserService.updateAvatar(email, avatarWebPath)

            if not result["success"]:
                # Nếu update DB lỗi thì xóa file mới vừa upload để tránh rác
                if os.path.exists(filePath):
                    os.remove(filePath)

                return jsonify(result), 400

            # Nếu update DB thành công thì xóa avatar cũ
            if oldAvatar:
                oldFilename = oldAvatar.replace("/static/img/admin/", "")

                # Không xóa avatar mặc định nếu có
                if oldFilename and "default" not in oldFilename.lower():
                    oldFilePath = os.path.join(uploadDir, oldFilename)

                    if os.path.exists(oldFilePath):
                        os.remove(oldFilePath)

            return jsonify(result), 200

        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Lỗi tải lên avatar: {str(e)}"
            }), 500
