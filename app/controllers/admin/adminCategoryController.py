from flask import jsonify, request

from app.services.admin.adminCategoryService import AdminCategoryService


class AdminCategoryController:

    @staticmethod
    def getCategoryList():
        try:
            filters = {
                "search": request.args.get("search", ""),
                "type": request.args.get("type", "ALL"),
                "status": request.args.get("status", "ALL"),
            }
            result = AdminCategoryService.getCategoryList(filters)
            statusCode = 200 if result["success"] else 400
            return jsonify(result), statusCode
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Lỗi lấy danh sách danh mục: {str(e)}",
                "data": None,
            }), 500

    @staticmethod
    def getCategoryDetail(id):
        try:
            result = AdminCategoryService.getCategoryDetail(id)
            statusCode = 200 if result["success"] else 404
            return jsonify(result), statusCode
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Lỗi lấy chi tiết danh mục: {str(e)}",
                "data": None,
            }), 500

    @staticmethod
    def createCategory():
        try:
            data = request.get_json() or {}
            result = AdminCategoryService.createCategory(data)
            statusCode = 201 if result["success"] else 400
            return jsonify(result), statusCode
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Lỗi thêm danh mục: {str(e)}",
                "data": None,
            }), 500

    @staticmethod
    def updateCategory(id):
        try:
            data = request.get_json() or {}
            result = AdminCategoryService.updateCategory(id, data)
            statusCode = 200 if result["success"] else 400
            return jsonify(result), statusCode
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Lỗi cập nhật danh mục: {str(e)}",
                "data": None,
            }), 500

    @staticmethod
    def toggleCategoryStatus(id):
        try:
            result = AdminCategoryService.toggleCategoryStatus(id)
            statusCode = 200 if result["success"] else 400
            return jsonify(result), statusCode
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Lỗi bật/tắt danh mục: {str(e)}",
                "data": None,
            }), 500
