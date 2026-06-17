from app import db


class DuLieuHuanLuyenAi(db.Model):
    __tablename__ = "du_lieu_huan_luyen_ai"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    moTa = db.Column("mo_ta", db.Text, nullable=False)
    idDanhMuc = db.Column("danh_muc_id", db.Integer, db.ForeignKey("danh_muc.id"), nullable=False)

    ngayTao = db.Column("ngay_tao", db.DateTime)

    def __repr__(self):
        return f"<DuLieuHuanLuyenAi {self.id}>"
