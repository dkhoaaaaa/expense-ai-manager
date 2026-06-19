from datetime import datetime
from decimal import Decimal

from sqlalchemy import case, func, or_

from app import db
from app.models.danhMucModel import DanhMuc
from app.models.giaoDichModel import GiaoDich
from app.models.nguoiDungModel import NguoiDung
from app.models.taiKhoanModel import TaiKhoan


class AdminTransactionService:
    VALID_TYPES = {"ALL", "THU", "CHI"}

    @staticmethod
    def getTransactionList(filters):
        validationResult = AdminTransactionService.validateFilters(filters)
        if not validationResult["success"]:
            return validationResult

        query = AdminTransactionService.baseQuery()
        query = AdminTransactionService.applyFilters(query, validationResult["data"])

        rows = query.order_by(GiaoDich.ngayGiaoDich.desc(), GiaoDich.id.desc()).all()
        transactions = [AdminTransactionService.buildTransactionItem(row) for row in rows]
        stats = AdminTransactionService.getTransactionStats(query)

        return {
            "success": True,
            "message": "Lay danh sach giao dich thanh cong",
            "data": {
                "transactions": transactions,
                "stats": stats,
                "categories": AdminTransactionService.getCategoryOptions(),
                "items": transactions,
                "summary": stats,
            },
        }

    @staticmethod
    def getTransactionDetail(id):
        row = AdminTransactionService.baseQuery().filter(GiaoDich.id == id).first()
        if not row:
            return {
                "success": False,
                "message": "Khong tim thay giao dich",
                "data": None,
            }

        return {
            "success": True,
            "message": "Lay chi tiet giao dich thanh cong",
            "data": AdminTransactionService.buildTransactionItem(row),
        }

    @staticmethod
    def getTransactionStats(query):
        statsRow = query.with_entities(
            func.count(GiaoDich.id).label("totalCount"),
            func.coalesce(
                func.sum(case((GiaoDich.loai == "THU", GiaoDich.soTien), else_=0)),
                0,
            ).label("totalIncome"),
            func.coalesce(
                func.sum(case((GiaoDich.loai == "CHI", GiaoDich.soTien), else_=0)),
                0,
            ).label("totalExpense"),
            func.sum(
                case((GiaoDich.phuongThucPhanLoai.in_(["RULE_BASED", "MACHINE_LEARNING"]), 1), else_=0)
            ).label("aiCount"),
        ).one()

        return {
            "totalCount": int(statsRow.totalCount or 0),
            "totalIncome": AdminTransactionService.toNumber(statsRow.totalIncome),
            "totalExpense": AdminTransactionService.toNumber(statsRow.totalExpense),
            "aiCount": int(statsRow.aiCount or 0),
        }

    @staticmethod
    def validateFilters(filters):
        transactionType = (filters.get("type") or "ALL").strip().upper()
        categoryIdText = (filters.get("categoryId") or "").strip()
        fromDateText = (filters.get("fromDate") or "").strip()
        toDateText = (filters.get("toDate") or "").strip()

        if transactionType not in AdminTransactionService.VALID_TYPES:
            return {
                "success": False,
                "message": "Loai giao dich khong hop le",
                "data": None,
            }

        categoryId = None
        if categoryIdText and categoryIdText != "ALL":
            try:
                categoryId = int(categoryIdText)
            except ValueError:
                return {
                    "success": False,
                    "message": "Danh muc loc khong hop le",
                    "data": None,
                }

            if categoryId <= 0:
                return {
                    "success": False,
                    "message": "Danh muc loc khong hop le",
                    "data": None,
                }

        fromDate = AdminTransactionService.parseDate(fromDateText)
        if fromDateText and fromDate is None:
            return {
                "success": False,
                "message": "fromDate phai dung dinh dang YYYY-MM-DD",
                "data": None,
            }

        toDate = AdminTransactionService.parseDate(toDateText)
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
                "type": transactionType,
                "categoryId": categoryId,
                "fromDate": fromDate,
                "toDate": toDate,
            },
        }

    @staticmethod
    def parseDate(value):
        if not value:
            return None

        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None

    @staticmethod
    def baseQuery():
        return (
            db.session.query(GiaoDich, TaiKhoan, NguoiDung, DanhMuc)
            .join(TaiKhoan, GiaoDich.idTK == TaiKhoan.id)
            .outerjoin(NguoiDung, NguoiDung.idTK == TaiKhoan.id)
            .outerjoin(DanhMuc, GiaoDich.idDanhMuc == DanhMuc.id)
        )

    @staticmethod
    def applyFilters(query, filters):
        search = filters["search"]

        if search:
            likeSearch = f"%{search}%"
            query = query.filter(
                or_(
                    TaiKhoan.email.ilike(likeSearch),
                    NguoiDung.hoTen.ilike(likeSearch),
                    DanhMuc.tenDanhMuc.ilike(likeSearch),
                    GiaoDich.moTa.ilike(likeSearch),
                )
            )

        if filters["type"] != "ALL":
            query = query.filter(GiaoDich.loai == filters["type"])

        if filters["categoryId"]:
            query = query.filter(GiaoDich.idDanhMuc == filters["categoryId"])

        if filters["fromDate"]:
            query = query.filter(GiaoDich.ngayGiaoDich >= filters["fromDate"])

        if filters["toDate"]:
            query = query.filter(GiaoDich.ngayGiaoDich <= filters["toDate"])

        return query

    @staticmethod
    def buildTransactionItem(row):
        transaction, taiKhoan, nguoiDung, danhMuc = row
        return {
            "id": transaction.id,
            "email": taiKhoan.email,
            "hoTen": nguoiDung.hoTen if nguoiDung else "",
            "danhMucId": danhMuc.id if danhMuc else None,
            "tenDanhMuc": danhMuc.tenDanhMuc if danhMuc else "",
            "loai": transaction.loai,
            "soTien": AdminTransactionService.toNumber(transaction.soTien),
            "moTa": transaction.moTa or "",
            "ngayGiaoDich": AdminTransactionService.formatDate(transaction.ngayGiaoDich),
            "phuongThucPhanLoai": transaction.phuongThucPhanLoai,
            "doTinCay": AdminTransactionService.toNumber(transaction.doTinCay),
        }

    @staticmethod
    def getCategoryOptions():
        categories = (
            DanhMuc.query
            .filter(DanhMuc.trangThai == "ACTIVE")
            .order_by(DanhMuc.loai.asc(), DanhMuc.tenDanhMuc.asc())
            .all()
        )
        return [
            {
                "id": category.id,
                "tenDanhMuc": category.tenDanhMuc,
                "loai": category.loai,
            }
            for category in categories
        ]

    @staticmethod
    def toNumber(value):
        if value is None:
            return 0
        if isinstance(value, Decimal):
            return float(value)
        return value

    @staticmethod
    def formatDate(value):
        return value.strftime("%Y-%m-%d") if value else None
