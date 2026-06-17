from app import db


class NguoiDung(db.Model):
    __tablename__ = "nguoi_dung"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idTK = db.Column("tai_khoan_id", db.Integer, db.ForeignKey("tai_khoan.id"), unique=True, nullable=False)

    hoTen = db.Column("ho_ten", db.String(100), nullable=False)
    gioiTinh = db.Column("gioi_tinh", db.Enum("NAM", "NU", "KHAC"), nullable=True)

    ngaySinh = db.Column("ngay_sinh", db.Date, nullable=True)
    sdt = db.Column("so_dien_thoai", db.String(20), nullable=True)

    avatar = db.Column("anh_dai_dien", db.String(255), nullable=True)

    ngayTao = db.Column("ngay_tao", db.DateTime)
    ngayCapNhat = db.Column("ngay_cap_nhat", db.DateTime)

    def __repr__(self):
        return f"<NguoiDung {self.hoTen}>"
