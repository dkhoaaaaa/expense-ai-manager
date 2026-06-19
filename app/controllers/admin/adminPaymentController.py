from flask import jsonify, request

from app.services.admin.adminPaymentService import AdminPaymentService


class AdminPaymentController:

    @staticmethod
    def getPaymentList():
        try:
            filters = {
                "search": request.args.get("search", ""),
                "status": request.args.get("status", "ALL"),
                "fromDate": request.args.get("fromDate", ""),
                "toDate": request.args.get("toDate", ""),
            }
            result = AdminPaymentService.getPaymentList(filters)
            statusCode = 200 if result["success"] else 400
            return jsonify(result), statusCode
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Loi lay danh sach thanh toan: {str(e)}",
                "data": None,
            }), 500

    @staticmethod
    def getPaymentDetail(id):
        try:
            result = AdminPaymentService.getPaymentDetail(id)
            statusCode = 200 if result["success"] else 404
            return jsonify(result), statusCode
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Loi lay chi tiet thanh toan: {str(e)}",
                "data": None,
            }), 500
