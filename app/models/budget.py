from app import db


class Budget(db.Model):
    __tablename__ = "budgets"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, nullable=False)

    category_id = db.Column(db.Integer, nullable=False)

    month = db.Column(db.Integer, nullable=False)

    year = db.Column(db.Integer, nullable=False)

    limit_amount = db.Column(db.Float, nullable=False)