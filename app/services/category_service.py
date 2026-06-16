from app.models.category import Category
from app import db


def get_categories():
    return Category.query.all()


def create_category(data):
    c = Category(name=data["name"])
    db.session.add(c)
    db.session.commit()
    return c