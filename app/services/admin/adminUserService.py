from datetime import date, datetime

from flask import request

from app import db
from app.models.nguoiDungModel import NguoiDung
from app.models.taiKhoanModel import TaiKhoan


class AdminUserService:

    @staticmethod
    def getAdminUser(email):
        taiKhoan = TaiKhoan.query.filter_by(email=email, vaiTro="ADMIN").first()

        if not taiKhoan:
            return {
                "success": False,
                "message": "Không tìm thấy tài khoản admin",
            }

        adUser = NguoiDung.query.filter_by(idTK=taiKhoan.id).first()

        if not adUser:
            return {
                "success": False,
                "message": "Không tìm thấy thông tin chi tiết admin",
            }

        return {
            "success": True,
            "admin": {
                "id": taiKhoan.id,
                "email": taiKhoan.email,
                "vaiTro": taiKhoan.vaiTro,
                "trangThai": taiKhoan.trangThai,
                "hoTen": adUser.hoTen,
                "sdt": adUser.sdt,
                "gioiTinh": adUser.gioiTinh,
                "ngaySinh": (
                    adUser.ngaySinh.strftime("%Y-%m-%d") if adUser.ngaySinh else None
                ),
                "avatar": adUser.avatar,
            },
        }

    @staticmethod
    def updateAdminUser(email):
        taiKhoan = TaiKhoan.query.filter_by(email=email, vaiTro="ADMIN").first()

        if not taiKhoan:
            return {
                "success": False,
                "message": "Không tìm thấy tài khoản admin",
            }

        adUser = NguoiDung.query.filter_by(idTK=taiKhoan.id).first()

        if not adUser:
            return {
                "success": False,
                "message": "Không tìm thấy thông tin chi tiết admin",
            }

        data = request.get_json() or {}

        validateResult = AdminUserService.validateUpdateAdminUser(data)

        if not validateResult["success"]:
            return validateResult

        validatedData = validateResult["data"]

        adUser.hoTen = validatedData["hoTen"]
        adUser.sdt = validatedData["sdt"]
        adUser.ngaySinh = validatedData["ngaySinh"]

        gioiTinh = data.get("gioiTinh")

        if gioiTinh is not None:
            adUser.gioiTinh = gioiTinh

        db.session.commit()

        return {
            "success": True,
            "message": "Cập nhật thông tin admin thành công",
            "admin": {
                "id": taiKhoan.id,
                "email": taiKhoan.email,
                "vaiTro": taiKhoan.vaiTro,
                "trangThai": taiKhoan.trangThai,
                "hoTen": adUser.hoTen,
                "sdt": adUser.sdt,
                "gioiTinh": adUser.gioiTinh,
                "ngaySinh": (
                    adUser.ngaySinh.strftime("%Y-%m-%d") if adUser.ngaySinh else None
                ),
                "avatar": adUser.avatar,
            },
        }

    @staticmethod
    def validateUpdateAdminUser(data):
        hoTen = data.get("hoTen")
        sdt = data.get("sdt")
        ngaySinhStr = data.get("ngaySinh")

        # Validate họ tên
        if hoTen is None:
            return {
                "success": False,
                "message": "Họ tên không được để trống",
            }

        hoTen = str(hoTen).strip()

        if not hoTen:
            return {
                "success": False,
                "message": "Họ tên không được để trống",
            }

        # Validate số điện thoại
        if sdt is None:
            return {
                "success": False,
                "message": "Số điện thoại không được để trống",
            }

        sdt = str(sdt).strip()

        if not sdt:
            return {
                "success": False,
                "message": "Số điện thoại không được để trống",
            }

        if not sdt.isdigit():
            return {
                "success": False,
                "message": "Số điện thoại chỉ được chứa chữ số",
            }

        if len(sdt) != 10:
            return {
                "success": False,
                "message": "Số điện thoại phải đủ 10 số",
            }

        # Validate ngày sinh
        ngaySinh = None

        if ngaySinhStr is not None and str(ngaySinhStr).strip() != "":
            ngaySinhStr = str(ngaySinhStr).strip()

            try:
                ngaySinh = datetime.strptime(ngaySinhStr, "%Y-%m-%d").date()
            except ValueError:
                return {
                    "success": False,
                    "message": "Định dạng ngày sinh không hợp lệ, yêu cầu YYYY-MM-DD",
                }

            if ngaySinh > date.today():
                return {
                    "success": False,
                    "message": "Ngày sinh không được lớn hơn ngày hiện tại",
                }

        return {
            "success": True,
            "message": "Dữ liệu hợp lệ",
            "data": {
                "hoTen": hoTen,
                "sdt": sdt,
                "ngaySinh": ngaySinh,
            },
        }

    @staticmethod
    def changePassword(email, currentPassword, newPassword, confirmPassword):
        # Validate đầu vào
        if not currentPassword or not newPassword or not confirmPassword:
            return {
                "success": False,
                "message": "Vui lòng nhập đầy đủ các trường mật khẩu",
            }

        if len(newPassword) < 6:
            return {"success": False, "message": "Mật khẩu mới phải có ít nhất 6 ký tự"}

        if newPassword != confirmPassword:
            return {"success": False, "message": "Mật khẩu xác nhận không khớp"}

        taiKhoan = TaiKhoan.query.filter_by(email=email).first()
        if taiKhoan is None:
            return {"success": False, "message": "Không tìm thấy tài khoản"}

        # Kiểm tra mật khẩu hiện tại
        if not taiKhoan.checkPassword(currentPassword):
            return {"success": False, "message": "Mật khẩu hiện tại không đúng"}

        # Không cho đặt trùng mật khẩu cũ
        if taiKhoan.checkPassword(newPassword):
            return {
                "success": False,
                "message": "Mật khẩu mới không được trùng với mật khẩu hiện tại",
            }

        # Hash và lưu
        taiKhoan.setPassword(newPassword)
        db.session.commit()

        return {"success": True, "message": "Đổi mật khẩu thành công"}

    @staticmethod
    def updateAvatar(email, avatarPath):
        taiKhoan = TaiKhoan.query.filter_by(email=email, vaiTro="ADMIN").first()
        if not taiKhoan:
            return {"success": False, "message": "Không tìm thấy tài khoản admin"}

        adUser = NguoiDung.query.filter_by(idTK=taiKhoan.id).first()
        if not adUser:
            return {"success": False, "message": "Không tìm thấy thông tin chi tiết admin"}

        adUser.avatar = avatarPath
        db.session.commit()

        return {    
            "success": True,
            "message": "Cập nhật ảnh đại diện thành công",
            "avatar": avatarPath
        }

    @staticmethod
    def getCurrentAvatar(email):
        taiKhoan = TaiKhoan.query.filter_by(email=email, vaiTro="ADMIN").first()

        if not taiKhoan:
            return None

        adminUser = NguoiDung.query.filter_by(idTK=taiKhoan.id).first()

        if not adminUser:
            return None

        return adminUser.avatar
