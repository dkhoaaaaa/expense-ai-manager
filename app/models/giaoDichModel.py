from sqlalchemy.orm import synonym
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime, date
from app import db


class CaseInsensitiveStr(str):
    def __eq__(self, other):
        if isinstance(other, str):
            return self.lower() == other.lower()
        return super().__eq__(other)
    
    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.lower())


class GiaoDich(db.Model):
    __tablename__ = "giao_dich"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    idTK = db.Column("tai_khoan_id", db.Integer, db.ForeignKey("tai_khoan.id"), nullable=False)
    idDanhMuc = db.Column("danh_muc_id", db.Integer, db.ForeignKey("danh_muc.id"), nullable=True)

    loai = db.Column(db.Enum("THU", "CHI"), nullable=False)
    soTien = db.Column("so_tien", db.Numeric(12, 2), nullable=False)

    moTa = db.Column("mo_ta", db.Text, nullable=True)
    ngayGiaoDich = db.Column("ngay_giao_dich", db.Date, nullable=False, default=date.today)

    phuongThucPhanLoai = db.Column(
        "phuong_thuc_phan_loai",
        db.Enum("THU_CONG", "RULE_BASED", "MACHINE_LEARNING"),
        default="THU_CONG",
    )
    doTinCay = db.Column("do_tin_cay", db.Numeric(5, 2), nullable=True)

    ngayTao = db.Column("ngay_tao", db.DateTime, default=datetime.utcnow)
    ngayCapNhat = db.Column("ngay_cap_nhat", db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Synonyms tương thích ngược với Transaction
    user_id = synonym("idTK")
    category_id = synonym("idDanhMuc")
    amount = synonym("soTien")
    description = synonym("moTa")
    created_at = synonym("ngayTao")

    # Hybrid property type tương thích ngược với Transaction.type
    @hybrid_property
    def type(self):
        return CaseInsensitiveStr("income" if self.loai == "THU" else "expense")

    @type.setter
    def type(self, value):
        val_upper = str(value).upper() if value else ""
        if val_upper in ("INCOME", "THU"):
            self.loai = "THU"
        elif val_upper in ("EXPENSE", "CHI"):
            self.loai = "CHI"
        else:
            self.loai = "CHI"

    @type.expression
    def type(cls):
        return db.case(
            (cls.loai == "THU", "income"),
            (cls.loai == "CHI", "expense"),
            else_=cls.loai
        )

    def __repr__(self):
        return f"<GiaoDich {self.soTien}>"
