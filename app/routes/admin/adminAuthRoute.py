from flask import Blueprint, render_template

from app.controllers.admin.adminAiController import AdminAiController
from app.controllers.admin.adminAuthController import AdminAuthController
from app.controllers.admin.adminCategoryController import AdminCategoryController
from app.controllers.admin.adminChatbotController import AdminChatbotController
from app.controllers.admin.adminDashboardController import AdminDashboardController
from app.controllers.admin.adminPaymentController import AdminPaymentController
from app.controllers.admin.adminPremiumController import AdminPremiumController
from app.controllers.admin.adminReportController import AdminReportController
from app.controllers.admin.adminTransactionController import AdminTransactionController
from app.controllers.admin.adminUserController import AdminUserController
from app.controllers.admin.adminUserManageController import AdminUserManageController
from app.middleware.admin.adminMiddleware import adminRequired

adminAuthRoute = Blueprint("adminAuthRoute", __name__, url_prefix="/admin")


@adminAuthRoute.route("/login", methods=["GET"])
def showLoginAdmin():
    return render_template("admin/loginAdmin.html")


@adminAuthRoute.route("/auth/login", methods=["POST"])
def loginAdmin():
    return AdminAuthController.loginAdmin()


@adminAuthRoute.route("/home", methods=["GET"])
def showHomeAdmin():
    return render_template("admin/homeAdmin.html")


@adminAuthRoute.route("/api/stats", methods=["GET"])
@adminRequired
def getStatsAdmin():
    return AdminDashboardController.getStats()


@adminAuthRoute.route("/api/profile", methods=["GET"])
@adminRequired
def getAdminProfile():
    return AdminUserController.getAdminProfile()


@adminAuthRoute.route("/api/profile", methods=["PATCH"])
@adminRequired
def updateAdminProfile():
    return AdminUserController.updateAdminProfile()


@adminAuthRoute.route("/api/profile/password", methods=["PATCH"])
@adminRequired
def changeAdminPassword():
    return AdminUserController.changePassword()


@adminAuthRoute.route("/api/profile/avatar", methods=["POST"])
@adminRequired
def uploadAdminAvatar():
    return AdminUserController.uploadAvatar()


# ==================== USER MANAGE ROUTES ====================

@adminAuthRoute.route("/api/users", methods=["GET"])
@adminRequired
def getUserList():
    return AdminUserManageController.getUserList()


@adminAuthRoute.route("/api/users/<int:id>", methods=["GET"])
@adminRequired
def getUserDetail(id):
    return AdminUserManageController.getUserDetail(id)


@adminAuthRoute.route("/api/users/<int:id>/ban", methods=["POST"])
@adminRequired
def banUser(id):
    return AdminUserManageController.banUser(id)


@adminAuthRoute.route("/api/users/<int:id>/unban", methods=["POST"])
@adminRequired
def unbanUser(id):
    return AdminUserManageController.unbanUser(id)


@adminAuthRoute.route("/api/users/<int:id>/change-role", methods=["POST"])
@adminRequired
def changeUserRole(id):
    return AdminUserManageController.changeUserRole(id)


@adminAuthRoute.route("/api/reports/export", methods=["POST"])
@adminRequired
def exportAdminReport():
    return AdminReportController.exportReport()


# ==================== CATEGORY ROUTES ====================

@adminAuthRoute.route("/api/categories", methods=["GET"])
@adminRequired
def getCategoryList():
    return AdminCategoryController.getCategoryList()


@adminAuthRoute.route("/api/categories/<int:id>", methods=["GET"])
@adminRequired
def getCategoryDetail(id):
    return AdminCategoryController.getCategoryDetail(id)


@adminAuthRoute.route("/api/categories", methods=["POST"])
@adminRequired
def createCategory():
    return AdminCategoryController.createCategory()


@adminAuthRoute.route("/api/categories/<int:id>", methods=["PATCH"])
@adminRequired
def updateCategory(id):
    return AdminCategoryController.updateCategory(id)


@adminAuthRoute.route("/api/categories/<int:id>/toggle-status", methods=["PATCH"])
@adminRequired
def toggleCategoryStatus(id):
    return AdminCategoryController.toggleCategoryStatus(id)


# ==================== TRANSACTION ROUTES ====================

@adminAuthRoute.route("/api/transactions", methods=["GET"])
@adminRequired
def getTransactionList():
    return AdminTransactionController.getTransactionList()


@adminAuthRoute.route("/api/transactions/<int:id>", methods=["GET"])
@adminRequired
def getTransactionDetail(id):
    return AdminTransactionController.getTransactionDetail(id)


# ==================== PREMIUM ROUTES ====================

@adminAuthRoute.route("/api/premium", methods=["GET"])
@adminRequired
def getPremiumList():
    return AdminPremiumController.getPremiumList()


@adminAuthRoute.route("/api/premium/<int:id>", methods=["GET"])
@adminRequired
def getPremiumDetail(id):
    return AdminPremiumController.getPremiumDetail(id)


@adminAuthRoute.route("/api/premium/<int:id>/extend", methods=["POST"])
@adminRequired
def extendPremium(id):
    return AdminPremiumController.extendPremium(id)


@adminAuthRoute.route("/api/premium/<int:id>/cancel", methods=["POST"])
@adminRequired
def cancelPremium(id):
    return AdminPremiumController.cancelPremium(id)


# ==================== PAYMENT ROUTES ====================

@adminAuthRoute.route("/api/payments", methods=["GET"])
@adminRequired
def getPaymentList():
    return AdminPaymentController.getPaymentList()


@adminAuthRoute.route("/api/payments/<int:id>", methods=["GET"])
@adminRequired
def getPaymentDetail(id):
    return AdminPaymentController.getPaymentDetail(id)


# ==================== CHATBOT ROUTES ====================

@adminAuthRoute.route("/api/chatbot/logs", methods=["GET"])
@adminRequired
def getChatbotLogs():
    return AdminChatbotController.getChatbotLogs()


@adminAuthRoute.route("/api/chatbot/logs/<int:id>", methods=["GET"])
@adminRequired
def getChatbotLogDetail(id):
    return AdminChatbotController.getChatbotLogDetail(id)


# ==================== AI ROUTES ====================

@adminAuthRoute.route("/api/ai/status", methods=["GET"])
@adminRequired
def getAiStatus():
    return AdminAiController.getAiStatus()


@adminAuthRoute.route("/api/ai/test", methods=["POST"])
@adminRequired
def testAiClassification():
    return AdminAiController.testAiClassification()


@adminAuthRoute.route("/api/ai/retrain", methods=["POST"])
@adminRequired
def retrainAiModel():
    return AdminAiController.retrainAiModel()
