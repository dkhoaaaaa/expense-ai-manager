from flask import jsonify

from app.services.admin.adminDashboardService import AdminDashboardService


class AdminDashboardController:

    @staticmethod
    def getStats():
        try:
            statsData = AdminDashboardService.getStats()
            return (
                jsonify(
                    {
                        "success": True,
                        "data": statsData,
                    }
                ),
                200,
            )
        except Exception as e:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Lỗi khi lấy thống kê: {str(e)}",
                    }
                ),
                500,
            )
