from app import db


class GiaoDich(db.Model):
    __tablename__ = "giao_dich"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    idTK = db.Column("tai_khoan_id", db.Integer, db.ForeignKey("tai_khoan.id"), nullable=False)
    idDanhMuc = db.Column("danh_muc_id", db.Integer, db.ForeignKey("danh_muc.id"), nullable=True)

    loai = db.Column(db.Enum("THU", "CHI"), nullable=False)
    soTien = db.Column("so_tien", db.Numeric(12, 2), nullable=False)

    moTa = db.Column("mo_ta", db.Text, nullable=True)
    ngayGiaoDich = db.Column("ngay_giao_dich", db.Date, nullable=False)

    phuongThucPhanLoai = db.Column(
        "phuong_thuc_phan_loai",
        db.Enum("THU_CONG", "RULE_BASED", "MACHINE_LEARNING"),
        default="THU_CONG",
    )
    doTinCay = db.Column("do_tin_cay", db.Numeric(5, 2), nullable=True)

    ngayTao = db.Column("ngay_tao", db.DateTime)
    ngayCapNhat = db.Column("ngay_cap_nhat", db.DateTime)

    def __repr__(self):
        return f"<GiaoDich {self.soTien}>"
