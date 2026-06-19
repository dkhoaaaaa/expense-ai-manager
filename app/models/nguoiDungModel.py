from sqlalchemy.orm import synonym
from app import db


class NguoiDung(db.Model):
    __tablename__ = "nguoi_dung"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idTK = db.Column("tai_khoan_id", db.Integer, db.ForeignKey("tai_khoan.id"), unique=True, nullable=False)

    hoTen = db.Column("ho_ten", db.String(100), nullable=False)
    gioiTinh = db.Column("gioi_tinh", db.Enum("NAM", "NU", "KHAC"), nullable=True)

    ngaySinh = db.Column("ngay_sinh", db.Date, nullable=True)
    sdt = db.Column("so_dien_thoai", db.String(20), nullable=True)

    avatar = db.Column("anh_dai_dien", db.String(255), nullable=True)

    ngayTao = db.Column("ngay_tao", db.DateTime)
    ngayCapNhat = db.Column("ngay_cap_nhat", db.DateTime)

    # Synonyms tương thích ngược
    tai_khoan_id = synonym("idTK")
    ho_ten = synonym("hoTen")
    gioi_tinh = synonym("gioiTinh")
    ngay_sinh = synonym("ngaySinh")
    so_dien_thoai = synonym("sdt")
    anh_dai_dien = synonym("avatar")
    ngay_tao = synonym("ngayTao")
    ngay_cap_nhat = synonym("ngayCapNhat")

    def __repr__(self):
        return f"<NguoiDung {self.hoTen}>"
