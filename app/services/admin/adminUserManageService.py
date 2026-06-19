from sqlalchemy import case, func, or_

from app import db
from app.models.nguoiDungModel import NguoiDung
from app.models.taiKhoanModel import TaiKhoan


class AdminUserManageService:
    VALID_FILTER_ROLES = {"ALL", "USER", "PREMIUM", "ADMIN"}
    VALID_ROLES = {"USER", "PREMIUM", "ADMIN"}
    VALID_FILTER_STATUSES = {"ALL", "ACTIVE", "BANNED"}
    VALID_STATUSES = {"ACTIVE", "BANNED"}

    @staticmethod
    def getUserList(filters):
        validationResult = AdminUserManageService.validateFilters(filters)
        if not validationResult["success"]:
            return validationResult

        query = AdminUserManageService.baseQuery()
        query = AdminUserManageService.applyFilters(query, validationResult["data"])

        rows = query.order_by(TaiKhoan.ngayTao.desc(), TaiKhoan.id.desc()).all()
        users = [AdminUserManageService.buildUserItem(row) for row in rows]
        stats = AdminUserManageService.getUserStats(query)

        return {
            "success": True,
            "message": "Lay danh sach nguoi dung thanh cong",
            "data": {
                "users": users,
                "stats": stats,
                "items": users,
                "summary": stats,
            },
        }

    @staticmethod
    def getUserDetail(id):
        row = AdminUserManageService.getUserRow(id)
        if not row:
            return {
                "success": False,
                "message": "Khong tim thay nguoi dung",
                "data": None,
            }

        return {
            "success": True,
            "message": "Lay chi tiet nguoi dung thanh cong",
            "data": AdminUserManageService.buildUserItem(row),
        }

    @staticmethod
    def banUser(id, currentAdminId):
        if str(id) == str(currentAdminId):
            return {
                "success": False,
                "message": "Khong the tu khoa tai khoan admin dang dang nhap",
                "data": None,
            }

        row = AdminUserManageService.getUserRow(id)
        if not row:
            return {
                "success": False,
                "message": "Khong tim thay nguoi dung",
                "data": None,
            }

        taiKhoan, _ = row
        taiKhoan.trangThai = "BANNED"
        db.session.commit()

        return {
            "success": True,
            "message": "Khoa tai khoan thanh cong",
            "data": AdminUserManageService.buildUserItem(AdminUserManageService.getUserRow(id)),
        }

    @staticmethod
    def unbanUser(id):
        row = AdminUserManageService.getUserRow(id)
        if not row:
            return {
                "success": False,
                "message": "Khong tim thay nguoi dung",
                "data": None,
            }

        taiKhoan, _ = row
        taiKhoan.trangThai = "ACTIVE"
        db.session.commit()

        return {
            "success": True,
            "message": "Mo khoa tai khoan thanh cong",
            "data": AdminUserManageService.buildUserItem(AdminUserManageService.getUserRow(id)),
        }

    @staticmethod
    def changeUserRole(id, role):
        role = (role or "").strip().upper()
        if role not in AdminUserManageService.VALID_ROLES:
            return {
                "success": False,
                "message": "Vai tro tai khoan khong hop le",
                "data": None,
            }

        row = AdminUserManageService.getUserRow(id)
        if not row:
            return {
                "success": False,
                "message": "Khong tim thay nguoi dung",
                "data": None,
            }

        taiKhoan, _ = row
        taiKhoan.vaiTro = role
        db.session.commit()

        return {
            "success": True,
            "message": "Doi vai tro tai khoan thanh cong",
            "data": AdminUserManageService.buildUserItem(AdminUserManageService.getUserRow(id)),
        }

    @staticmethod
    def getUserStats(query):
        statsRow = query.with_entities(
            func.count(TaiKhoan.id).label("totalCount"),
            func.sum(case((TaiKhoan.vaiTro == "USER", 1), else_=0)).label("normalUserCount"),
            func.sum(case((TaiKhoan.vaiTro == "PREMIUM", 1), else_=0)).label("premiumUserCount"),
            func.sum(case((TaiKhoan.trangThai == "BANNED", 1), else_=0)).label("bannedUserCount"),
        ).one()

        return {
            "totalCount": int(statsRow.totalCount or 0),
            "normalUserCount": int(statsRow.normalUserCount or 0),
            "premiumUserCount": int(statsRow.premiumUserCount or 0),
            "bannedUserCount": int(statsRow.bannedUserCount or 0),
        }

    @staticmethod
    def validateFilters(filters):
        role = (filters.get("role") or "ALL").strip().upper()
        status = (filters.get("status") or "ALL").strip().upper()

        if role not in AdminUserManageService.VALID_FILTER_ROLES:
            return {
                "success": False,
                "message": "Vai tro loc khong hop le",
                "data": None,
            }

        if status not in AdminUserManageService.VALID_FILTER_STATUSES:
            return {
                "success": False,
                "message": "Trang thai loc khong hop le",
                "data": None,
            }

        return {
            "success": True,
            "message": "Bo loc hop le",
            "data": {
                "search": (filters.get("search") or "").strip(),
                "role": role,
                "status": status,
            },
        }

    @staticmethod
    def baseQuery():
        return (
            db.session.query(TaiKhoan, NguoiDung)
            .outerjoin(NguoiDung, NguoiDung.idTK == TaiKhoan.id)
        )

    @staticmethod
    def applyFilters(query, filters):
        search = filters["search"]
        role = filters["role"]
        status = filters["status"]

        if search:
            likeSearch = f"%{search}%"
            query = query.filter(
                or_(
                    TaiKhoan.email.ilike(likeSearch),
                    NguoiDung.hoTen.ilike(likeSearch),
                )
            )

        if role != "ALL":
            query = query.filter(TaiKhoan.vaiTro == role)

        if status != "ALL":
            query = query.filter(TaiKhoan.trangThai == status)

        return query

    @staticmethod
    def getUserRow(id):
        return (
            AdminUserManageService.baseQuery()
            .filter(TaiKhoan.id == id)
            .first()
        )

    @staticmethod
    def buildUserItem(row):
        taiKhoan, nguoiDung = row
        return {
            "id": taiKhoan.id,
            "email": taiKhoan.email,
            "hoTen": nguoiDung.hoTen if nguoiDung else "",
            "vaiTro": taiKhoan.vaiTro,
            "trangThai": taiKhoan.trangThai,
            "ngayTao": AdminUserManageService.formatDateTime(taiKhoan.ngayTao),
        }

    @staticmethod
    def formatDateTime(value):
        return value.strftime("%Y-%m-%d %H:%M:%S") if value else None
