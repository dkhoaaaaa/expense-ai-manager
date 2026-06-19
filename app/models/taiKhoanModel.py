from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.orm import synonym
from app import db


class TaiKhoan(db.Model):
    __tablename__ = "tai_khoan"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    email = db.Column(db.String(100), nullable=False, unique=True)
    matKhauHash = db.Column("mat_khau_hash", db.String(255), nullable=False)

    vaiTro = db.Column("vai_tro", db.Enum("USER", "PREMIUM", "ADMIN"), default="USER")
    trangThai = db.Column("trang_thai", db.Enum("ACTIVE", "BANNED"), default="ACTIVE")

    ngayTao = db.Column("ngay_tao", db.DateTime)
    ngayCapNhat = db.Column("ngay_cap_nhat", db.DateTime)

    # Relationship tương thích ngược
    nguoi_dung = db.relationship('NguoiDung', backref='tai_khoan', uselist=False, cascade='all, delete-orphan')

    # Synonyms tương thích ngược
    mat_khau_hash = synonym("matKhauHash")
    vai_tro = synonym("vaiTro")
    trang_thai = synonym("trangThai")
    ngay_tao = synonym("ngayTao")
    ngay_cap_nhat = synonym("ngayCapNhat")

    def setPassword(self, password):
        self.matKhauHash = generate_password_hash(password)

    def checkPassword(self, password):
        return check_password_hash(self.matKhauHash, password)

    def __repr__(self):
        return f"<TaiKhoan {self.email}>"
