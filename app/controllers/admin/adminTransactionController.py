from flask import jsonify, request

from app.services.admin.adminTransactionService import AdminTransactionService


class AdminTransactionController:

    @staticmethod
    def getTransactionList():
        try:
            filters = {
                "search": request.args.get("search", ""),
                "type": request.args.get("type", "ALL"),
                "categoryId": request.args.get("categoryId", ""),
                "fromDate": request.args.get("fromDate", ""),
                "toDate": request.args.get("toDate", ""),
            }
            result = AdminTransactionService.getTransactionList(filters)
            statusCode = 200 if result["success"] else 400
            return jsonify(result), statusCode
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Loi lay danh sach giao dich: {str(e)}",
                "data": None,
            }), 500

    @staticmethod
    def getTransactionDetail(id):
        try:
            result = AdminTransactionService.getTransactionDetail(id)
            statusCode = 200 if result["success"] else 404
            return jsonify(result), statusCode
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Loi lay chi tiet giao dich: {str(e)}",
                "data": None,
            }), 500
