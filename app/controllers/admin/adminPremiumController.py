from flask import jsonify, request

from app.services.admin.adminPremiumService import AdminPremiumService


class AdminPremiumController:

    @staticmethod
    def getPremiumList():
        try:
            filters = {
                "search": request.args.get("search", ""),
                "status": request.args.get("status", "ALL"),
            }
            result = AdminPremiumService.getPremiumList(filters)
            statusCode = 200 if result["success"] else 400
            return jsonify(result), statusCode
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Loi lay danh sach Premium: {str(e)}",
                "data": None,
            }), 500

    @staticmethod
    def getPremiumDetail(id):
        try:
            result = AdminPremiumService.getPremiumDetail(id)
            statusCode = 200 if result["success"] else 404
            return jsonify(result), statusCode
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Loi lay chi tiet Premium: {str(e)}",
                "data": None,
            }), 500

    @staticmethod
    def extendPremium(id):
        try:
            data = request.get_json() or {}
            result = AdminPremiumService.extendPremium(id, data.get("months"))
            statusCode = 200 if result["success"] else 400
            return jsonify(result), statusCode
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Loi gia han Premium: {str(e)}",
                "data": None,
            }), 500

    @staticmethod
    def cancelPremium(id):
        try:
            result = AdminPremiumService.cancelPremium(id)
            statusCode = 200 if result["success"] else 400
            return jsonify(result), statusCode
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Loi huy Premium: {str(e)}",
                "data": None,
            }), 500
