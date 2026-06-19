from flask import jsonify, request

from app.services.admin.adminChatbotService import AdminChatbotService


class AdminChatbotController:

    @staticmethod
    def getChatbotLogs():
        try:
            filters = {
                "search": request.args.get("search", ""),
                "sender": request.args.get("sender", "ALL"),
                "fromDate": request.args.get("fromDate", ""),
                "toDate": request.args.get("toDate", ""),
            }
            result = AdminChatbotService.getChatbotLogs(filters)
            statusCode = 200 if result["success"] else 400
            return jsonify(result), statusCode
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Lỗi lấy danh sách chatbot logs: {str(e)}",
                "data": None,
            }), 500

    @staticmethod
    def getChatbotLogDetail(id):
        try:
            result = AdminChatbotService.getChatbotLogDetail(id)
            statusCode = 200 if result["success"] else 404
            return jsonify(result), statusCode
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Lỗi lấy chi tiết chatbot log: {str(e)}",
                "data": None,
            }), 500
