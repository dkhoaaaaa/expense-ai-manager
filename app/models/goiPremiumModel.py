from sqlalchemy.orm import synonym
from app import db


class GoiPremium(db.Model):
    __tablename__ = "goi_premium"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    idTK = db.Column("tai_khoan_id", db.Integer, db.ForeignKey("tai_khoan.id"), nullable=False)

    tenGoi = db.Column("ten_goi", db.String(50), default="PREMIUM")
    gia = db.Column(db.Numeric(12, 2), nullable=False)

    trangThai = db.Column("trang_thai", db.Enum("ACTIVE", "EXPIRED", "CANCELLED"), default="ACTIVE")

    ngayBatDau = db.Column("ngay_bat_dau", db.DateTime)
    ngayKetThuc = db.Column("ngay_ket_thuc", db.DateTime, nullable=False)

    ngayTao = db.Column("ngay_tao", db.DateTime)

    # Synonyms tương thích ngược
    tai_khoan_id = synonym("idTK")
    ten_goi = synonym("tenGoi")
    trang_thai = synonym("trangThai")
    ngay_bat_dau = synonym("ngayBatDau")
    ngay_ket_thuc = synonym("ngayKetThuc")
    ngay_tao = synonym("ngayTao")

    def __repr__(self):
        return f"<GoiPremium {self.tenGoi}>"

