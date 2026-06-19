from sqlalchemy.orm import synonym
from app import db


class DanhMuc(db.Model):
    __tablename__ = "danh_muc"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    tenDanhMuc = db.Column("ten_danh_muc", db.String(100), nullable=False)
    loai = db.Column(db.Enum("THU", "CHI"), nullable=False, default="CHI")
    keywordAI = db.Column("keyword_ai", db.Text, nullable=True)
    trangThai = db.Column("trang_thai", db.Enum("ACTIVE", "INACTIVE"), default="ACTIVE")

    ngayTao = db.Column("ngay_tao", db.DateTime)

    # Synonym tương thích ngược với Category
    name = synonym("tenDanhMuc")

    def __repr__(self):
        return f"<DanhMuc {self.tenDanhMuc}>"
