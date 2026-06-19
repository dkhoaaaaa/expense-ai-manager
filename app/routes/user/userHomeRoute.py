from flask import Blueprint, render_template, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from app.controllers.user.userHomeController import UserHomeController

userHomeRoute = Blueprint("userHomeRoute", __name__)


@userHomeRoute.route("/home", methods=["GET"])
def showHome():
    return render_template("user/home.html")


@userHomeRoute.route("/api/home-data", methods=["GET"])
def getHomeData():
    return UserHomeController.getHomeData()


@userHomeRoute.route("/home/content/<tab>", methods=["GET"])
@jwt_required(optional=True)
def getHomeContent(tab):
    # Mapping data-tab to template path relative to template_folder
    mapping = {
        "overview": "user/home.html",
        "transactions": "user/transaction.html",
        "budgets": "user/budget.html",
        "ai-hub": "user/ai.html",
        "profile": "user/profile.html"
    }
    
    template_path = mapping.get(tab)
    if not template_path:
        return render_empty_state()

    # Check if the template file exists
    template_dir = os.path.join(current_app.root_path, current_app.template_folder or "views/templates")
    full_path = os.path.join(template_dir, template_path)
    
    if not os.path.exists(full_path):
        return render_empty_state()
        
    kwargs = {}
    if tab == "profile":
        # Profile template requires 'account'
        user_id = get_jwt_identity()
        if user_id:
            from app.models.taiKhoanModel import TaiKhoan
            current_user = TaiKhoan.query.get(int(user_id))
            kwargs["account"] = current_user
            
    kwargs["partial"] = True

    return render_template(template_path, **kwargs)


def render_empty_state():
    return """
<div class="empty-state">
    <i class="bi bi-folder-x"></i>
    <h3>Chức năng chưa được phát triển</h3>
    <p>Hiện tại chưa có giao diện cho mục này.</p>
</div>
"""
