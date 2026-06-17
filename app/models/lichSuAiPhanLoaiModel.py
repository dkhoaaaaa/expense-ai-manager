from app import db


class LichSuAiPhanLoai(db.Model):
    __tablename__ = "lich_su_ai_phan_loai"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    idTK = db.Column("tai_khoan_id", db.Integer, db.ForeignKey("tai_khoan.id"), nullable=False)

    vanBanNhap = db.Column("van_ban_nhap", db.Text, nullable=True)
    idDanhMucDuDoan = db.Column(
        "danh_muc_du_doan_id",
        db.Integer,
        db.ForeignKey("danh_muc.id"),
        nullable=True,
    )

    doTinCay = db.Column("do_tin_cay", db.Numeric(5, 2), nullable=True)
    tenModel = db.Column("ten_model", db.String(100), nullable=True)

    ngayTao = db.Column("ngay_tao", db.DateTime)

    def __repr__(self):
        return f"<LichSuAiPhanLoai {self.id}>"
