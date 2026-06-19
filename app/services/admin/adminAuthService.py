from app.models.taiKhoanModel import TaiKhoan


class AdminAuthService:

    @staticmethod
    def loginAdmin(email, password):
        taiKhoan = TaiKhoan.query.filter_by(email=email).first()

        if taiKhoan is None:
            return {"success": False, "message": "Email không tồn tại"}

        if not taiKhoan.checkPassword(password):
            return {"success": False, "message": "Mật khẩu không đúng"}

        if taiKhoan.vaiTro != "ADMIN":
            return {"success": False, "message": "Tài khoản này không có quyền Admin"}

        if taiKhoan.trangThai != "ACTIVE":
            return {
                "success": False,
                "message": "Tài khoản đã bị khóa",
            }

        return {
            "success": True,
            "message": "Đăng nhập Admin thành công",
            "data": {
                "id": taiKhoan.id,
                "email": taiKhoan.email,
                "vaiTro": taiKhoan.vaiTro,
                "trangThai": taiKhoan.trangThai,
            },
        }
