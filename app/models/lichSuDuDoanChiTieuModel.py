from app import db


class LichSuDuDoanChiTieu(db.Model):
    __tablename__ = "lich_su_du_doan_chi_tieu"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    idTK = db.Column("tai_khoan_id", db.Integer, db.ForeignKey("tai_khoan.id"), nullable=False)

    thangDuDoan = db.Column("thang_du_doan", db.Integer, nullable=False)
    namDuDoan = db.Column("nam_du_doan", db.Integer, nullable=False)

    soTienDuDoan = db.Column("so_tien_du_doan", db.Numeric(12, 2), nullable=False)
    doTinCay = db.Column("do_tin_cay", db.Numeric(5, 2), nullable=True)

    xuHuong = db.Column("xu_huong", db.Enum("TANG", "GIAM", "ON_DINH"), nullable=True)

    ngayTao = db.Column("ngay_tao", db.DateTime)

    def __repr__(self):
        return f"<LichSuDuDoanChiTieu {self.thangDuDoan}/{self.namDuDoan}>"
