from datetime import datetime
from decimal import Decimal

from sqlalchemy import case, func, or_

from app import db
from app.models.goiPremiumModel import GoiPremium
from app.models.nguoiDungModel import NguoiDung
from app.models.taiKhoanModel import TaiKhoan
from app.models.thanhToanModel import ThanhToan


class AdminPaymentService:
    VALID_STATUSES = {"ALL", "SUCCESS", "PENDING", "FAILED"}

    @staticmethod
    def getPaymentList(filters):
        validationResult = AdminPaymentService.validateFilters(filters)
        if not validationResult["success"]:
            return validationResult

        query = AdminPaymentService.baseQuery()
        query = AdminPaymentService.applyFilters(query, validationResult["data"])

        rows = query.order_by(
            func.coalesce(ThanhToan.ngayThanhToan, ThanhToan.ngayTao).desc(),
            ThanhToan.id.desc(),
        ).all()

        payments = [AdminPaymentService.buildPaymentItem(row) for row in rows]
        stats = AdminPaymentService.getPaymentStats(query)

        return {
            "success": True,
            "message": "Lay danh sach thanh toan thanh cong",
            "data": {
                "payments": payments,
                "stats": stats,
                "items": payments,
                "summary": stats,
            },
        }

    @staticmethod
    def getPaymentDetail(id):
        row = AdminPaymentService.baseQuery().filter(ThanhToan.id == id).first()
        if not row:
            return {
                "success": False,
                "message": "Khong tim thay thanh toan",
                "data": None,
            }

        return {
            "success": True,
            "message": "Lay chi tiet thanh toan thanh cong",
            "data": AdminPaymentService.buildPaymentItem(row),
        }

    @staticmethod
    def getPaymentStats(query):
        successRevenueExpression = case(
            (ThanhToan.trangThaiThanhToan == "SUCCESS", ThanhToan.soTien),
            else_=0,
        )
        statsRow = query.with_entities(
            func.coalesce(func.sum(successRevenueExpression), 0).label("totalRevenue"),
            func.sum(case((ThanhToan.trangThaiThanhToan == "SUCCESS", 1), else_=0)).label("successCount"),
            func.sum(case((ThanhToan.trangThaiThanhToan == "PENDING", 1), else_=0)).label("pendingCount"),
            func.sum(case((ThanhToan.trangThaiThanhToan == "FAILED", 1), else_=0)).label("failedCount"),
        ).one()

        return {
            "totalRevenue": AdminPaymentService.toNumber(statsRow.totalRevenue),
            "successCount": int(statsRow.successCount or 0),
            "pendingCount": int(statsRow.pendingCount or 0),
            "failedCount": int(statsRow.failedCount or 0),
        }

    @staticmethod
    def validateFilters(filters):
        status = (filters.get("status") or "ALL").strip().upper()
        fromDateText = (filters.get("fromDate") or "").strip()
        toDateText = (filters.get("toDate") or "").strip()

        if status not in AdminPaymentService.VALID_STATUSES:
            return {
                "success": False,
                "message": "Trang thai thanh toan khong hop le",
                "data": None,
            }

        fromDate = AdminPaymentService.parseDate(fromDateText, "fromDate")
        if fromDateText and fromDate is None:
            return {
                "success": False,
                "message": "fromDate phai dung dinh dang YYYY-MM-DD",
                "data": None,
            }

        toDate = AdminPaymentService.parseDate(toDateText, "toDate")
        if toDateText and toDate is None:
            return {
                "success": False,
                "message": "toDate phai dung dinh dang YYYY-MM-DD",
                "data": None,
            }

        if fromDate and toDate and fromDate > toDate:
            return {
                "success": False,
                "message": "fromDate khong duoc lon hon toDate",
                "data": None,
            }

        return {
            "success": True,
            "message": "Bo loc hop le",
            "data": {
                "search": (filters.get("search") or "").strip(),
                "status": status,
                "fromDate": fromDate,
                "toDate": toDate,
            },
        }

    @staticmethod
    def parseDate(value, fieldName):
        if not value:
            return None

        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None

    @staticmethod
    def baseQuery():
        return (
            db.session.query(ThanhToan, TaiKhoan, NguoiDung, GoiPremium)
            .join(TaiKhoan, ThanhToan.idTK == TaiKhoan.id)
            .outerjoin(NguoiDung, NguoiDung.idTK == TaiKhoan.id)
            .outerjoin(GoiPremium, ThanhToan.idGoiPremium == GoiPremium.id)
        )

    @staticmethod
    def applyFilters(query, filters):
        search = filters["search"]
        status = filters["status"]
        paymentDate = func.date(func.coalesce(ThanhToan.ngayThanhToan, ThanhToan.ngayTao))

        if search:
            likeSearch = f"%{search}%"
            query = query.filter(
                or_(
                    TaiKhoan.email.ilike(likeSearch),
                    NguoiDung.hoTen.ilike(likeSearch),
                    ThanhToan.maGiaoDich.ilike(likeSearch),
                )
            )

        if status != "ALL":
            query = query.filter(ThanhToan.trangThaiThanhToan == status)

        if filters["fromDate"]:
            query = query.filter(paymentDate >= filters["fromDate"])

        if filters["toDate"]:
            query = query.filter(paymentDate <= filters["toDate"])

        return query

    @staticmethod
    def buildPaymentItem(row):
        payment, taiKhoan, nguoiDung, premium = row
        return {
            "id": payment.id,
            "maGiaoDich": payment.maGiaoDich,
            "email": taiKhoan.email,
            "hoTen": nguoiDung.hoTen if nguoiDung else "",
            "soTien": AdminPaymentService.toNumber(payment.soTien),
            "phuongThucThanhToan": payment.phuongThucThanhToan,
            "trangThaiThanhToan": payment.trangThaiThanhToan,
            "ngayThanhToan": AdminPaymentService.formatDateTime(payment.ngayThanhToan),
            "ngayTao": AdminPaymentService.formatDateTime(payment.ngayTao),
            "tenGoi": premium.tenGoi if premium else None,
        }

    @staticmethod
    def toNumber(value):
        if value is None:
            return 0
        if isinstance(value, Decimal):
            return float(value)
        return value

    @staticmethod
    def formatDateTime(value):
        return value.strftime("%Y-%m-%d %H:%M:%S") if value else None
