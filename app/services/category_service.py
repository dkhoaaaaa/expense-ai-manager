from app.models.category import Category
from app import db


def get_categories():
    return Category.query.all()


def create_category(data):
    c = Category(name=data["name"])
    db.session.add(c)
    db.session.commit()
    return c

def update_category(category_id, data):
    c = Category.query.get(category_id)

    if not c:
        return None

    c.name = data["name"]

    db.session.commit()
    return c


def delete_category(category_id):
    c = Category.query.get(category_id)

    if not c:
        return None

    db.session.delete(c)
    db.session.commit()

    return True