from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity

from app.services.admin.adminUserManageService import AdminUserManageService


class AdminUserManageController:

    @staticmethod
    def getUserList():
        try:
            filters = {
                "search": request.args.get("search", ""),
                "role": request.args.get("role", "ALL"),
                "status": request.args.get("status", "ALL"),
            }
            result = AdminUserManageService.getUserList(filters)
            statusCode = 200 if result["success"] else 400
            return jsonify(result), statusCode
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Loi lay danh sach nguoi dung: {str(e)}",
                "data": None,
            }), 500

    @staticmethod
    def getUserDetail(id):
        try:
            result = AdminUserManageService.getUserDetail(id)
            statusCode = 200 if result["success"] else 404
            return jsonify(result), statusCode
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Loi lay chi tiet nguoi dung: {str(e)}",
                "data": None,
            }), 500

    @staticmethod
    def banUser(id):
        try:
            currentAdminId = get_jwt_identity()
            result = AdminUserManageService.banUser(id, currentAdminId)
            statusCode = 200 if result["success"] else 400
            return jsonify(result), statusCode
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Loi khoa tai khoan: {str(e)}",
                "data": None,
            }), 500

    @staticmethod
    def unbanUser(id):
        try:
            result = AdminUserManageService.unbanUser(id)
            statusCode = 200 if result["success"] else 400
            return jsonify(result), statusCode
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Loi mo khoa tai khoan: {str(e)}",
                "data": None,
            }), 500

    @staticmethod
    def changeUserRole(id):
        try:
            data = request.get_json() or {}
            result = AdminUserManageService.changeUserRole(id, data.get("role"))
            statusCode = 200 if result["success"] else 400
            return jsonify(result), statusCode
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Loi doi vai tro tai khoan: {str(e)}",
                "data": None,
            }), 500
