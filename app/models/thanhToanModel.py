from app import db


class ThanhToan(db.Model):
    __tablename__ = "thanh_toan"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    idTK = db.Column("tai_khoan_id", db.Integer, db.ForeignKey("tai_khoan.id"), nullable=False)
    idGoiPremium = db.Column("goi_premium_id", db.Integer, db.ForeignKey("goi_premium.id"), nullable=True)

    soTien = db.Column("so_tien", db.Numeric(12, 2), nullable=False)
    phuongThucThanhToan = db.Column("phuong_thuc_thanh_toan", db.String(50), nullable=True)

    trangThaiThanhToan = db.Column(
        "trang_thai_thanh_toan",
        db.Enum("PENDING", "SUCCESS", "FAILED"),
        default="PENDING",
    )
    maGiaoDich = db.Column("ma_giao_dich", db.String(100), nullable=True)

    ngayThanhToan = db.Column("ngay_thanh_toan", db.DateTime, nullable=True)
    ngayTao = db.Column("ngay_tao", db.DateTime)

    def __repr__(self):
        return f"<ThanhToan {self.maGiaoDich}>"
