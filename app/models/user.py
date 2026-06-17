from app import db
from datetime import datetime

class TaiKhoan(db.Model):
    __tablename__ = 'tai_khoan'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    mat_khau_hash = db.Column(db.String(255), nullable=False)
    vai_tro = db.Column(db.Enum('USER', 'PREMIUM', 'ADMIN'), default='USER')
    trang_thai = db.Column(db.Enum('ACTIVE', 'BANNED'), default='ACTIVE')
    ngay_tao = db.Column(db.DateTime, default=datetime.utcnow)
    ngay_cap_nhat = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Liên kết với bảng NguoiDung (quan hệ 1-1)
    nguoi_dung = db.relationship('NguoiDung', backref='tai_khoan', uselist=False, cascade='all, delete-orphan')


class NguoiDung(db.Model):
    __tablename__ = 'nguoi_dung'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tai_khoan_id = db.Column(db.Integer, db.ForeignKey('tai_khoan.id', ondelete='CASCADE'), nullable=False, unique=True)
    ho_ten = db.Column(db.String(100), nullable=False)
    so_dien_thoai = db.Column(db.String(20))
    ngay_sinh = db.Column(db.Date)
    gioi_tinh = db.Column(db.Enum('NAM', 'NU', 'KHAC'))
    anh_dai_dien = db.Column(db.String(255))
    ngay_tao = db.Column(db.DateTime, default=datetime.utcnow)
    ngay_cap_nhat = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
