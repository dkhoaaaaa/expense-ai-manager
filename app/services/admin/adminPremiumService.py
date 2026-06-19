import calendar
from datetime import datetime, timedelta

from sqlalchemy import case, func, or_

from app import db
from app.models.goiPremiumModel import GoiPremium
from app.models.nguoiDungModel import NguoiDung
from app.models.taiKhoanModel import TaiKhoan


class AdminPremiumService:
    VALID_STATUSES = {"ALL", "ACTIVE", "EXPIRED", "CANCELLED"}

    @staticmethod
    def getPremiumList(filters):
        AdminPremiumService.syncExpiredPremium()

        validationResult = AdminPremiumService.validateFilters(filters)
        if not validationResult["success"]:
            return validationResult

        query = AdminPremiumService.baseQuery()
        query = AdminPremiumService.applyFilters(query, validationResult["data"])

        rows = query.order_by(GoiPremium.ngayKetThuc.desc(), GoiPremium.id.desc()).all()
        premiumList = [AdminPremiumService.buildPremiumItem(row) for row in rows]
        stats = AdminPremiumService.getPremiumStats(query)

        return {
            "success": True,
            "message": "Lay danh sach Premium thanh cong",
            "data": {
                "premiumList": premiumList,
                "stats": stats,
                "items": premiumList,
                "summary": stats,
            },
        }

    @staticmethod
    def getPremiumDetail(id):
        AdminPremiumService.syncExpiredPremium()

        row = AdminPremiumService.getPremiumRow(id)
        if not row:
            return {
                "success": False,
                "message": "Khong tim thay goi Premium",
                "data": None,
            }

        return {
            "success": True,
            "message": "Lay chi tiet Premium thanh cong",
            "data": AdminPremiumService.buildPremiumItem(row),
        }

    @staticmethod
    def extendPremium(id, months):
        AdminPremiumService.syncExpiredPremium()

        parsedMonths = AdminPremiumService.parseMonths(months)
        if parsedMonths is None:
            return {
                "success": False,
                "message": "So thang gia han phai la so nguyen lon hon 0",
                "data": None,
            }

        row = AdminPremiumService.getPremiumRow(id)
        if not row:
            return {
                "success": False,
                "message": "Khong tim thay goi Premium",
                "data": None,
            }

        premium, taiKhoan, _ = row
        now = datetime.now()
        baseDate = premium.ngayKetThuc if premium.trangThai == "ACTIVE" and premium.ngayKetThuc and premium.ngayKetThuc > now else now

        premium.ngayKetThuc = AdminPremiumService.addMonths(baseDate, parsedMonths)
        premium.trangThai = "ACTIVE"
        taiKhoan.vaiTro = "PREMIUM"

        db.session.commit()

        return {
            "success": True,
            "message": "Gia han Premium thanh cong",
            "data": AdminPremiumService.buildPremiumItem(AdminPremiumService.getPremiumRow(id)),
        }

    @staticmethod
    def cancelPremium(id):
        AdminPremiumService.syncExpiredPremium()

        row = AdminPremiumService.getPremiumRow(id)
        if not row:
            return {
                "success": False,
                "message": "Khong tim thay goi Premium",
                "data": None,
            }

        premium, taiKhoan, _ = row
        premium.trangThai = "CANCELLED"
        taiKhoan.vaiTro = "USER"

        db.session.commit()

        return {
            "success": True,
            "message": "Huy Premium thanh cong",
            "data": AdminPremiumService.buildPremiumItem(AdminPremiumService.getPremiumRow(id)),
        }

    @staticmethod
    def getPremiumStats(query):
        now = datetime.now()
        expiringDate = now + timedelta(days=7)

        statsRow = query.with_entities(
            func.sum(case((GoiPremium.trangThai == "ACTIVE", 1), else_=0)).label("activeCount"),
            func.sum(
                case(
                    (
                        (GoiPremium.trangThai == "ACTIVE")
                        & (GoiPremium.ngayKetThuc >= now)
                        & (GoiPremium.ngayKetThuc <= expiringDate),
                        1,
                    ),
                    else_=0,
                )
            ).label("expiringCount"),
            func.sum(case((GoiPremium.trangThai.in_(["EXPIRED", "CANCELLED"]), 1), else_=0)).label("expiredCount"),
        ).one()

        return {
            "activeCount": int(statsRow.activeCount or 0),
            "expiringCount": int(statsRow.expiringCount or 0),
            "expiredCount": int(statsRow.expiredCount or 0),
            "expiringSoonCount": int(statsRow.expiringCount or 0),
            "inactiveCount": int(statsRow.expiredCount or 0),
        }

    @staticmethod
    def validateFilters(filters):
        status = (filters.get("status") or "ALL").strip().upper()

        if status not in AdminPremiumService.VALID_STATUSES:
            return {
                "success": False,
                "message": "Trang thai Premium khong hop le",
                "data": None,
            }

        return {
            "success": True,
            "message": "Bo loc hop le",
            "data": {
                "search": (filters.get("search") or "").strip(),
                "status": status,
            },
        }

    @staticmethod
    def baseQuery():
        return (
            db.session.query(GoiPremium, TaiKhoan, NguoiDung)
            .join(TaiKhoan, GoiPremium.idTK == TaiKhoan.id)
            .outerjoin(NguoiDung, NguoiDung.idTK == TaiKhoan.id)
        )

    @staticmethod
    def applyFilters(query, filters):
        search = filters["search"]
        status = filters["status"]

        if search:
            likeSearch = f"%{search}%"
            query = query.filter(
                or_(
                    TaiKhoan.email.ilike(likeSearch),
                    NguoiDung.hoTen.ilike(likeSearch),
                )
            )

        if status != "ALL":
            query = query.filter(GoiPremium.trangThai == status)

        return query

    @staticmethod
    def syncExpiredPremium():
        now = datetime.now()
        expiredPremiums = GoiPremium.query.filter(
            GoiPremium.trangThai == "ACTIVE",
            GoiPremium.ngayKetThuc < now,
        ).all()

        if not expiredPremiums:
            return

        for premium in expiredPremiums:
            premium.trangThai = "EXPIRED"
            taiKhoan = TaiKhoan.query.get(premium.idTK)
            if taiKhoan and taiKhoan.vaiTro == "PREMIUM":
                taiKhoan.vaiTro = "USER"

        db.session.commit()

    @staticmethod
    def getPremiumRow(id):
        return (
            AdminPremiumService.baseQuery()
            .filter(GoiPremium.id == id)
            .first()
        )

    @staticmethod
    def buildPremiumItem(row):
        premium, taiKhoan, nguoiDung = row
        return {
            "id": premium.id,
            "taiKhoanId": taiKhoan.id,
            "email": taiKhoan.email,
            "hoTen": nguoiDung.hoTen if nguoiDung else "",
            "tenGoi": premium.tenGoi,
            "trangThai": premium.trangThai,
            "ngayBatDau": AdminPremiumService.formatDateTime(premium.ngayBatDau),
            "ngayKetThuc": AdminPremiumService.formatDateTime(premium.ngayKetThuc),
        }

    @staticmethod
    def parseMonths(value):
        try:
            months = int(value)
        except (TypeError, ValueError):
            return None

        if months <= 0:
            return None

        return months

    @staticmethod
    def addMonths(value, months):
        monthIndex = value.month - 1 + months
        year = value.year + monthIndex // 12
        month = monthIndex % 12 + 1
        day = min(value.day, calendar.monthrange(year, month)[1])
        return value.replace(year=year, month=month, day=day)

    @staticmethod
    def formatDateTime(value):
        return value.strftime("%Y-%m-%d %H:%M:%S") if value else None
