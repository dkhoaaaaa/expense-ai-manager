from app import db


class TinNhanChatbot(db.Model):
    __tablename__ = "tin_nhan_chatbot"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    idTK = db.Column("tai_khoan_id", db.Integer, db.ForeignKey("tai_khoan.id"), nullable=False)

    nguoiGui = db.Column("nguoi_gui", db.Enum("USER", "BOT"), nullable=False)
    noiDung = db.Column("noi_dung", db.Text, nullable=False)

    ngayTao = db.Column("ngay_tao", db.DateTime)

    def __repr__(self):
        return f"<TinNhanChatbot {self.nguoiGui}>"
