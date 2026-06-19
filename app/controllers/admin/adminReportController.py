from flask import jsonify, request, send_file

from app.services.admin.adminReportService import AdminReportService


class AdminReportController:

    @staticmethod
    def exportReport():
        try:
            payload = request.get_json(silent=True) or {}
            fileBytes, filename, mimetype = AdminReportService.buildReport(
                reportType=payload.get("report_type") or payload.get("reportType"),
                fileFormat=payload.get("format"),
                fromDate=payload.get("from_date") or payload.get("fromDate"),
                toDate=payload.get("to_date") or payload.get("toDate"),
            )

            return send_file(
                fileBytes,
                mimetype=mimetype,
                as_attachment=True,
                download_name=filename,
            )
        except ValueError as exc:
            return jsonify({"success": False, "message": str(exc)}), 400
        except Exception as exc:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Loi khi xuat bao cao: {str(exc)}",
                    }
                ),
                500,
            )

    @staticmethod
    def exportReportByType(reportType):
        try:
            fileBytes, filename, mimetype = AdminReportService.buildReport(
                reportType=reportType,
                fileFormat=request.args.get("format", "excel"),
                fromDate=request.args.get("fromDate") or request.args.get("from_date"),
                toDate=request.args.get("toDate") or request.args.get("to_date"),
            )

            return send_file(
                fileBytes,
                mimetype=mimetype,
                as_attachment=True,
                download_name=filename,
            )
        except ValueError as exc:
            return jsonify({"success": False, "message": str(exc), "data": None}), 400
        except Exception as exc:
            return jsonify({"success": False, "message": f"Lỗi khi xuất báo cáo: {str(exc)}", "data": None}), 500
