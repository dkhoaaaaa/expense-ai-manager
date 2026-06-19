from sqlalchemy.orm import synonym
from app import db


class NganSach(db.Model):
    __tablename__ = "ngan_sach"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    idTK = db.Column("tai_khoan_id", db.Integer, db.ForeignKey("tai_khoan.id"), nullable=False)
    idDanhMuc = db.Column("danh_muc_id", db.Integer, db.ForeignKey("danh_muc.id"), nullable=True)

    thang = db.Column(db.Integer, nullable=False)
    nam = db.Column(db.Integer, nullable=False)
    hanMuc = db.Column("han_muc", db.Numeric(12, 2), nullable=False)

    ngayTao = db.Column("ngay_tao", db.DateTime)

    # Synonyms tương thích ngược với Budget
    user_id = synonym("idTK")
    category_id = synonym("idDanhMuc")
    month = synonym("thang")
    year = synonym("nam")
    limit_amount = synonym("hanMuc")

    def __repr__(self):
        return f"<NganSach {self.thang}/{self.nam}>"
