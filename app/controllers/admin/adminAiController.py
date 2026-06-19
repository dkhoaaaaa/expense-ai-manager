from flask import jsonify, request

from app.services.admin.adminAiService import AdminAiService


class AdminAiController:

    @staticmethod
    def getAiStatus():
        try:
            result = AdminAiService.getAiStatus()
            statusCode = 200 if result["success"] else 400
            return jsonify(result), statusCode
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Lỗi lấy trạng thái AI Model: {str(e)}",
                "data": None,
            }), 500

    @staticmethod
    def testAiClassification():
        try:
            data = request.get_json() or {}
            result = AdminAiService.testClassification(data.get("text"))
            statusCode = 200 if result["success"] else 400
            return jsonify(result), statusCode
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Lỗi test phân loại AI: {str(e)}",
                "data": None,
            }), 500

    @staticmethod
    def retrainAiModel():
        try:
            result = AdminAiService.retrainModel()
            statusCode = 200 if result["success"] else 400
            return jsonify(result), statusCode
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Lỗi huấn luyện lại AI Model: {str(e)}",
                "data": None,
            }), 500
