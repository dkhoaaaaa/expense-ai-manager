from app import db
from datetime import datetime


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, nullable=False)

    amount = db.Column(db.Float, nullable=False)

    type = db.Column(db.String(20), nullable=False)  # INCOME / EXPENSE

    category_id = db.Column(db.Integer, nullable=False)

    description = db.Column(db.String(255))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)