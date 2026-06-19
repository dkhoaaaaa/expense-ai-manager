from sqlalchemy import case, func, or_

from app import db
from app.models.danhMucModel import DanhMuc
from app.models.giaoDichModel import GiaoDich


class AdminCategoryService:
    VALID_FILTER_TYPES = {"ALL", "THU", "CHI"}
    VALID_FILTER_STATUSES = {"ALL", "ACTIVE", "INACTIVE"}
    VALID_TYPES = {"THU", "CHI"}
    VALID_STATUSES = {"ACTIVE", "INACTIVE"}

    @staticmethod
    def getCategoryList(filters):
        validationResult = AdminCategoryService.validateFilters(filters)
        if not validationResult["success"]:
            return validationResult

        query = AdminCategoryService.baseQuery()
        query = AdminCategoryService.applyFilters(query, validationResult["data"])

        rows = query.order_by(DanhMuc.loai.asc(), DanhMuc.tenDanhMuc.asc()).all()
        categories = [AdminCategoryService.buildCategoryItem(row) for row in rows]

        return {
            "success": True,
            "message": "Lấy danh sách danh mục thành công",
            "data": {
                "categories": categories,
                "stats": AdminCategoryService.getCategoryStats(query),
            },
        }

    @staticmethod
    def getCategoryDetail(id):
        row = AdminCategoryService.getCategoryRow(id)
        if not row:
            return {
                "success": False,
                "message": "Không tìm thấy danh mục",
                "data": None,
            }

        return {
            "success": True,
            "message": "Lấy chi tiết danh mục thành công",
            "data": AdminCategoryService.buildCategoryItem(row),
        }

    @staticmethod
    def createCategory(data):
        validationResult = AdminCategoryService.validateCategoryData(data)
        if not validationResult["success"]:
            return validationResult

        categoryData = validationResult["data"]
        duplicatedCategory = AdminCategoryService.findDuplicateCategory(
            categoryData["name"], categoryData["type"]
        )
        if duplicatedCategory:
            return {
                "success": False,
                "message": "Tên danh mục đã tồn tại trong cùng loại",
                "data": None,
            }

        category = DanhMuc(
            tenDanhMuc=categoryData["name"],
            loai=categoryData["type"],
            keywordAI=categoryData["keywordAi"],
            trangThai=categoryData["status"],
        )

        db.session.add(category)
        db.session.commit()

        return {
            "success": True,
            "message": "Thêm danh mục thành công",
            "data": AdminCategoryService.buildCategoryItem(
                AdminCategoryService.getCategoryRow(category.id)
            ),
        }

    @staticmethod
    def updateCategory(id, data):
        category = DanhMuc.query.get(id)
        if not category:
            return {
                "success": False,
                "message": "Không tìm thấy danh mục",
                "data": None,
            }

        updateData = dict(data)
        updateData.setdefault("status", category.trangThai)

        validationResult = AdminCategoryService.validateCategoryData(updateData)
        if not validationResult["success"]:
            return validationResult

        categoryData = validationResult["data"]
        duplicatedCategory = AdminCategoryService.findDuplicateCategory(
            categoryData["name"], categoryData["type"], excludeId=id
        )
        if duplicatedCategory:
            return {
                "success": False,
                "message": "Tên danh mục đã tồn tại trong cùng loại",
                "data": None,
            }

        category.tenDanhMuc = categoryData["name"]
        category.loai = categoryData["type"]
        category.keywordAI = categoryData["keywordAi"]
        category.trangThai = categoryData["status"]
        db.session.commit()

        return {
            "success": True,
            "message": "Cập nhật danh mục thành công",
            "data": AdminCategoryService.buildCategoryItem(
                AdminCategoryService.getCategoryRow(id)
            ),
        }

    @staticmethod
    def toggleCategoryStatus(id):
        category = DanhMuc.query.get(id)
        if not category:
            return {
                "success": False,
                "message": "Không tìm thấy danh mục",
                "data": None,
            }

        category.trangThai = "INACTIVE" if category.trangThai == "ACTIVE" else "ACTIVE"
        db.session.commit()

        return {
            "success": True,
            "message": "Cập nhật trạng thái danh mục thành công",
            "data": AdminCategoryService.buildCategoryItem(
                AdminCategoryService.getCategoryRow(id)
            ),
        }

    @staticmethod
    def validateFilters(filters):
        categoryType = (filters.get("type") or "ALL").strip().upper()
        status = (filters.get("status") or "ALL").strip().upper()

        if categoryType not in AdminCategoryService.VALID_FILTER_TYPES:
            return {
                "success": False,
                "message": "Loại danh mục không hợp lệ",
                "data": None,
            }

        if status not in AdminCategoryService.VALID_FILTER_STATUSES:
            return {
                "success": False,
                "message": "Trạng thái danh mục không hợp lệ",
                "data": None,
            }

        return {
            "success": True,
            "message": "Bộ lọc hợp lệ",
            "data": {
                "search": (filters.get("search") or "").strip(),
                "type": categoryType,
                "status": status,
            },
        }

    @staticmethod
    def validateCategoryData(data):
        name = (data.get("name") or "").strip()
        categoryType = (data.get("type") or "").strip().upper()
        keywordAi = (data.get("keywordAi") or "").strip()
        status = (data.get("status") or "ACTIVE").strip().upper()

        if not name:
            return {
                "success": False,
                "message": "Tên danh mục không được trống",
                "data": None,
            }

        if categoryType not in AdminCategoryService.VALID_TYPES:
            return {
                "success": False,
                "message": "Loại danh mục chỉ nhận THU hoặc CHI",
                "data": None,
            }

        if status not in AdminCategoryService.VALID_STATUSES:
            return {
                "success": False,
                "message": "Trạng thái chỉ nhận ACTIVE hoặc INACTIVE",
                "data": None,
            }

        return {
            "success": True,
            "message": "Dữ liệu hợp lệ",
            "data": {
                "name": name,
                "type": categoryType,
                "keywordAi": keywordAi,
                "status": status,
            },
        }

    @staticmethod
    def baseQuery():
        transactionCount = func.count(GiaoDich.id).label("transactionCount")
        return (
            db.session.query(DanhMuc, transactionCount)
            .outerjoin(GiaoDich, GiaoDich.idDanhMuc == DanhMuc.id)
            .group_by(DanhMuc.id)
        )

    @staticmethod
    def applyFilters(query, filters):
        search = filters["search"]

        if search:
            likeSearch = f"%{search}%"
            query = query.filter(
                or_(
                    DanhMuc.tenDanhMuc.ilike(likeSearch),
                    DanhMuc.keywordAI.ilike(likeSearch),
                )
            )

        if filters["type"] != "ALL":
            query = query.filter(DanhMuc.loai == filters["type"])

        if filters["status"] != "ALL":
            query = query.filter(DanhMuc.trangThai == filters["status"])

        return query

    @staticmethod
    def getCategoryStats(query):
        categorySubquery = query.with_entities(
            DanhMuc.id.label("id"),
            DanhMuc.loai.label("loai"),
            DanhMuc.trangThai.label("trangThai"),
        ).subquery()

        statsRow = db.session.query(
            func.count(categorySubquery.c.id).label("totalCount"),
            func.sum(case((categorySubquery.c.loai == "THU", 1), else_=0)).label("incomeCount"),
            func.sum(case((categorySubquery.c.loai == "CHI", 1), else_=0)).label("expenseCount"),
            func.sum(case((categorySubquery.c.trangThai == "ACTIVE", 1), else_=0)).label("activeCount"),
        ).one()

        return {
            "totalCount": int(statsRow.totalCount or 0),
            "incomeCount": int(statsRow.incomeCount or 0),
            "expenseCount": int(statsRow.expenseCount or 0),
            "activeCount": int(statsRow.activeCount or 0),
        }

    @staticmethod
    def findDuplicateCategory(name, categoryType, excludeId=None):
        query = DanhMuc.query.filter(
            func.lower(DanhMuc.tenDanhMuc) == name.lower(),
            DanhMuc.loai == categoryType,
        )

        if excludeId:
            query = query.filter(DanhMuc.id != excludeId)

        return query.first()

    @staticmethod
    def getCategoryRow(id):
        return AdminCategoryService.baseQuery().filter(DanhMuc.id == id).first()

    @staticmethod
    def buildCategoryItem(row):
        category, transactionCount = row
        return {
            "id": category.id,
            "name": category.tenDanhMuc,
            "tenDanhMuc": category.tenDanhMuc,
            "type": category.loai,
            "loai": category.loai,
            "keywordAi": category.keywordAI or "",
            "keywordAI": category.keywordAI or "",
            "status": category.trangThai,
            "trangThai": category.trangThai,
            "transactionCount": int(transactionCount or 0),
            "ngayTao": AdminCategoryService.formatDateTime(category.ngayTao),
        }

    @staticmethod
    def formatDateTime(value):
        return value.strftime("%Y-%m-%d %H:%M:%S") if value else None
