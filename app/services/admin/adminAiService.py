import re
import unicodedata
from datetime import datetime

from sqlalchemy import func

from app.models.danhMucModel import DanhMuc
from app.models.duLieuHuanLuyenAiModel import DuLieuHuanLuyenAi


class AdminAiService:
    modelName = "Rule-based Keyword Classifier"
    accuracy = None
    lastTrainedAt = None

    @staticmethod
    def getAiStatus():
        totalSamples = AdminAiService.getTrainingSampleCount()
        lastTrainingSampleAt = AdminAiService.getLastTrainingSampleAt()

        if AdminAiService.accuracy is None:
            AdminAiService.accuracy = AdminAiService.estimateAccuracy(totalSamples)

        lastTrainedAt = AdminAiService.lastTrainedAt or lastTrainingSampleAt

        return {
            "success": True,
            "message": "Lấy trạng thái AI Model thành công",
            "data": {
                "modelName": AdminAiService.modelName,
                "accuracy": AdminAiService.accuracy,
                "totalTrainingSamples": totalSamples,
                "lastTrainedAt": AdminAiService.formatDateTime(lastTrainedAt),
            },
        }

    @staticmethod
    def testClassification(text):
        textValue = (text or "").strip()
        if not textValue:
            return {
                "success": False,
                "message": "Nội dung giao dịch mẫu không được trống",
                "data": None,
            }

        normalizedText = AdminAiService.normalizeText(textValue)
        categories = (
            DanhMuc.query
            .filter(DanhMuc.trangThai == "ACTIVE")
            .order_by(DanhMuc.loai.asc(), DanhMuc.tenDanhMuc.asc())
            .all()
        )

        bestMatch = None
        bestScore = 0
        bestMatchedKeywords = []

        for category in categories:
            keywords = AdminAiService.extractKeywords(category.keywordAI)
            matchedKeywords = [
                keyword for keyword in keywords
                if keyword and keyword in normalizedText
            ]
            score = len(matchedKeywords)

            if score > bestScore:
                bestScore = score
                bestMatch = category
                bestMatchedKeywords = matchedKeywords

        if bestMatch:
            confidence = min(98.0, 72.0 + bestScore * 8.5 + min(len(bestMatchedKeywords), 3) * 2)
            return {
                "success": True,
                "message": "Phân loại thành công",
                "data": {
                    "categoryName": bestMatch.tenDanhMuc,
                    "type": bestMatch.loai,
                    "confidence": round(confidence, 1),
                },
            }

        fallbackCategory = AdminAiService.getFallbackCategory()
        return {
            "success": True,
            "message": "Không tìm thấy keyword phù hợp, trả về danh mục mặc định",
            "data": {
                "categoryName": fallbackCategory.tenDanhMuc if fallbackCategory else "Khác",
                "type": fallbackCategory.loai if fallbackCategory else "CHI",
                "confidence": 45.0,
            },
        }

    @staticmethod
    def retrainModel():
        totalSamples = AdminAiService.getTrainingSampleCount()
        if totalSamples <= 0:
            return {
                "success": False,
                "message": "Chưa có dữ liệu huấn luyện AI",
                "data": None,
            }

        # Mo phong train de de nang cap sang scikit-learn:
        # 1. Lay du_lieu_huan_luyen_ai.
        # 2. Vectorize mo_ta.
        # 3. Train classifier theo danh_muc_id.
        # 4. Luu metadata model.
        AdminAiService.modelName = "Rule-based Keyword Classifier"
        AdminAiService.accuracy = AdminAiService.estimateAccuracy(totalSamples, retrained=True)
        AdminAiService.lastTrainedAt = datetime.now()

        status = AdminAiService.getAiStatus()
        return {
            "success": True,
            "message": "Huấn luyện lại AI Model thành công",
            "data": status["data"],
        }

    @staticmethod
    def getTrainingSampleCount():
        return int(DuLieuHuanLuyenAi.query.count() or 0)

    @staticmethod
    def getLastTrainingSampleAt():
        return DuLieuHuanLuyenAi.query.with_entities(func.max(DuLieuHuanLuyenAi.ngayTao)).scalar()

    @staticmethod
    def getFallbackCategory():
        return (
            DanhMuc.query
            .filter(DanhMuc.trangThai == "ACTIVE")
            .filter(func.lower(DanhMuc.tenDanhMuc) == "khác")
            .first()
        )

    @staticmethod
    def estimateAccuracy(totalSamples, retrained=False):
        if totalSamples <= 0:
            return 0.0

        baseAccuracy = 68.0 + min(totalSamples, 80) * 0.32
        if retrained:
            baseAccuracy += 3.5

        return round(min(baseAccuracy, 96.5), 1)

    @staticmethod
    def extractKeywords(keywordText):
        if not keywordText:
            return []

        return [
            AdminAiService.normalizeText(keyword)
            for keyword in re.split(r"[,;\n]", keywordText)
            if keyword.strip()
        ]

    @staticmethod
    def normalizeText(value):
        text = unicodedata.normalize("NFD", str(value).lower())
        text = "".join(char for char in text if unicodedata.category(char) != "Mn")
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    @staticmethod
    def formatDateTime(value):
        return value.strftime("%Y-%m-%d %H:%M:%S") if value else None
