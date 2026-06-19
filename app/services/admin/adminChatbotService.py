from datetime import datetime, time

from sqlalchemy import or_

from app import db
from app.models.nguoiDungModel import NguoiDung
from app.models.taiKhoanModel import TaiKhoan
from app.models.tinNhanChatbotModel import TinNhanChatbot


class AdminChatbotService:
    VALID_SENDERS = {"ALL", "USER", "BOT"}

    @staticmethod
    def getChatbotLogs(filters):
        validationResult = AdminChatbotService.validateFilters(filters)
        if not validationResult["success"]:
            return validationResult

        query = AdminChatbotService.baseQuery()
        query = AdminChatbotService.applyFilters(query, validationResult["data"])

        rows = query.order_by(TinNhanChatbot.ngayTao.desc(), TinNhanChatbot.id.desc()).all()
        logs = [AdminChatbotService.buildLogItem(row) for row in rows]

        return {
            "success": True,
            "message": "Lấy danh sách chatbot logs thành công",
            "data": {
                "logs": logs,
                "items": logs,
            },
        }

    @staticmethod
    def getChatbotLogDetail(id):
        row = AdminChatbotService.getLogRow(id)
        if not row:
            return {
                "success": False,
                "message": "Không tìm thấy chatbot log",
                "data": None,
            }

        return {
            "success": True,
            "message": "Lấy chi tiết chatbot log thành công",
            "data": AdminChatbotService.buildLogItem(row),
        }

    @staticmethod
    def validateFilters(filters):
        sender = (filters.get("sender") or "ALL").strip().upper()
        fromDateText = (filters.get("fromDate") or "").strip()
        toDateText = (filters.get("toDate") or "").strip()

        if sender not in AdminChatbotService.VALID_SENDERS:
            return {
                "success": False,
                "message": "Người gửi chỉ nhận ALL, USER hoặc BOT",
                "data": None,
            }

        fromDate = AdminChatbotService.parseDate(fromDateText)
        if fromDateText and fromDate is None:
            return {
                "success": False,
                "message": "fromDate phải đúng định dạng YYYY-MM-DD",
                "data": None,
            }

        toDate = AdminChatbotService.parseDate(toDateText)
        if toDateText and toDate is None:
            return {
                "success": False,
                "message": "toDate phải đúng định dạng YYYY-MM-DD",
                "data": None,
            }

        if fromDate and toDate and fromDate > toDate:
            return {
                "success": False,
                "message": "fromDate không được lớn hơn toDate",
                "data": None,
            }

        return {
            "success": True,
            "message": "Bộ lọc hợp lệ",
            "data": {
                "search": (filters.get("search") or "").strip(),
                "sender": sender,
                "fromDate": fromDate,
                "toDate": toDate,
            },
        }

    @staticmethod
    def baseQuery():
        return (
            db.session.query(TinNhanChatbot, TaiKhoan, NguoiDung)
            .join(TaiKhoan, TinNhanChatbot.idTK == TaiKhoan.id)
            .outerjoin(NguoiDung, NguoiDung.idTK == TaiKhoan.id)
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
                    TinNhanChatbot.noiDung.ilike(likeSearch),
                )
            )

        if filters["sender"] != "ALL":
            query = query.filter(TinNhanChatbot.nguoiGui == filters["sender"])

        if filters["fromDate"]:
            query = query.filter(
                TinNhanChatbot.ngayTao >= datetime.combine(filters["fromDate"], time.min)
            )

        if filters["toDate"]:
            query = query.filter(
                TinNhanChatbot.ngayTao <= datetime.combine(filters["toDate"], time.max)
            )

        return query

    @staticmethod
    def getLogRow(id):
        return AdminChatbotService.baseQuery().filter(TinNhanChatbot.id == id).first()

    @staticmethod
    def buildLogItem(row):
        log, account, user = row
        return {
            "id": log.id,
            "accountId": account.id,
            "email": account.email,
            "fullName": user.hoTen if user else "",
            "hoTen": user.hoTen if user else "",
            "sender": log.nguoiGui,
            "nguoiGui": log.nguoiGui,
            "content": log.noiDung,
            "noiDung": log.noiDung,
            "createdAt": AdminChatbotService.formatDateTime(log.ngayTao),
            "ngayTao": AdminChatbotService.formatDateTime(log.ngayTao),
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
    def formatDateTime(value):
        return value.strftime("%Y-%m-%d %H:%M:%S") if value else None
